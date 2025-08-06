import os
import time
import paramiko
from .sound import play_chirp_signal
from .clean import clean_wav
from .config import config
from .runtime_config import runtime_config
import socket
import threading
import sounddevice as sd
import numpy as np
import queue
from .utils import get_broadcast_address

MIC_NAME = "dmic_sv_shared"
CHANNEL_FMT = "stereo"
SAMPLING_RATE = 48000

ssh: paramiko.SSHClient = None
micro_signal_thread = None
file_name = ""
broadcast_received = False

def is_ssh_connected():
    global ssh
    if ssh is not None and ssh.get_transport() and ssh.get_transport().is_active():
        return True
    return False


def ssh_connect(hostname, port, username, password, socketio_instance):
    global ssh, micro_signal_thread
    try:
        ssh = paramiko.SSHClient()
        print(config['connection'])
        print("Connecting to RaspberryPi...")
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port, username, password, timeout=10)
        if not ssh.get_transport() or not ssh.get_transport().is_active():
            ssh = None
            print("SSH transport is not active.")
            return

        print('CONNECTED TO RASPBERRYPI')
    except Exception as e:
        print("SSH connection error:", e)
        ssh = None
        return

    try:
        with ssh.open_sftp() as sftp:
            sftp.put(os.path.join(os.path.dirname(__file__), "asoundrc.txt"), "/home/pi/.asoundrc")
            sftp.put(os.path.join(os.path.dirname(__file__), "pc_ip.txt"), "/home/pi/pc_ip.txt")
            sftp.put(os.path.join(os.path.dirname(__file__), "micro_signal_sender.py"), "/home/pi/micro_signal_sender.py")
            print(f"SFPT setup upload completed.")
    except Exception as e:
        print(f"SFPT setup upload error.", e)
        ssh = None
        return

    if not micro_signal_thread or not micro_signal_thread.is_alive():
        threading.Thread(target=listen_for_micro_signals, args=(socketio_instance,), daemon=True).start()

    time.sleep(1)
    start_micro_signal_sending()
    


def on_rec_start(connection, socketio_instance, output_filename):
    print("Executing 'on_rec_start': Starting micro on needle")
    global ssh
    global file_name

    file_name = output_filename

    if ssh is None:
        ssh_connect(*connection, socketio_instance=socketio_instance)
        time.sleep(1)

    if ssh:
        print("Recording started")
        remote_path = f"{config['remote_dir']}/{file_name}"
        mkdir_commad = f"mkdir {os.path.dirname(remote_path)}"
        ssh.exec_command(mkdir_commad)

        setup_command = f"echo 'DEVICE={MIC_NAME}\nDURATION=10\nSAMPLE_RATE={SAMPLING_RATE}\n" \
                        f"CHANNELS=2\nOUTPUT_FILE={remote_path}\nFORMAT=S32_LE' > " \
                        f"{config['remote_dir']}/recording_setup.txt"
        print("Setup command ====================================================================== \n")
        print(setup_command)
        ssh.exec_command(setup_command)
        time.sleep(0.01)

        start_command = f"bash -c 'source {config['remote_dir']}/recording_setup.txt && nohup arecord " \
                        f"-D $DEVICE -r $SAMPLE_RATE -c $CHANNELS -f $FORMAT -t wav -V {CHANNEL_FMT} " \
                        f"$OUTPUT_FILE &'"
        print("Start command ===================================================================== \n")
        print(start_command)
        ssh.exec_command(start_command)
        play_chirp_signal()
    else:
        return False
    
    return True

def kill_rasp_process():
    if ssh is not None:
        print("Killing process on RaspberryPi")
        stop_command = f"kill -INT $(ps aux | grep '[a]record -D {MIC_NAME}' | awk '{{print $2}}')"
        ssh.exec_command(stop_command)

def on_rec_stop(delete=False):
    global ssh
    global file_name
    recorded_files = []
    if ssh is not None:
        print("Recording stopped on RaspberryPi")
        stop_command = f"kill -INT $(ps aux | grep '[a]record -D {MIC_NAME}' | awk '{{print $2}}')"
        ssh.exec_command(stop_command)

        remote_path = f"{config['remote_dir']}/{file_name}"
        local_path = os.path.join(config["local_dir"], file_name)
        os.makedirs(config["local_dir"], exist_ok=True)

        try:
            with ssh.open_sftp() as sftp:
                sftp.get(remote_path, local_path)
        except Exception as e:
            print(f"SFPT download error. (remote '{remote_path}', local '{local_path}'.", e)

        recording_status = os.path.isfile(local_path) and os.path.getsize(local_path)
        if recording_status:
            recorded_files = clean_wav(local_path, os.path.dirname(local_path), offset=0.02)

        if delete:
            delete_command = f"rm {remote_path}"
            ssh.exec_command(delete_command)
    else:
        print("SSH not connected during stopping recording")
        return False
    
    return len(recorded_files) > 0


def delete_last_recording():
    global file_name
    deleted = []
    for file in [file_name, file_name[:-len(".wav")] + ".raw.wav"]:
        file = os.path.join(config["local_dir"], file)
        if os.path.exists(file):
            os.remove(file)
            deleted.append(file)
            print(file, "deleted")
        else:
            print(file, "does not exist")
    return deleted

def start_micro_signal_sending():
    print("Starting micro signal sending on RaspberryPi")
    command = "python3 -u /home/pi/micro_signal_sender.py"
    ssh.exec_command(command)

def listen_for_micro_signals(sio):
        global micro_signal_thread, broadcast_received
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', 5001))
        s.listen(1)
        print("Waiting for connection to micro signal server...")
        s.settimeout(10)
        try:
            conn, addr = s.accept()
            print(f"Connection from {addr}")
            broadcast_received = True
            micro_signal_thread = threading.Thread(target=receive_and_send_micro_signals, args=(conn, sio,), daemon=True).start()
        except socket.timeout:
            print("No connection received within timeout period.")

        print("Finished thread for listening to connection from raspberrypi")

def receive_and_send_micro_signals(conn, sio):
        
        buffer = b''
        frame_size = 512 * 8
        batch_frames = 25
        sample_rate = 48000

        warmup_done = False
        warmup_target_frames = int(0.1 * sample_rate)

        current_output_index = None
        output_stream = None
        audio_queue = queue.Queue()

        def audio_callback(outdata, frames, time_info, status):
            try:
                data = audio_queue.get_nowait()
            except queue.Empty:
                outdata[:] = np.zeros((frames, 2), dtype=np.float32)
                return
            
            if data.shape[0] < frames:
                outdata[:data.shape[0], :] = data
                outdata[data.shape[0]:, :] = 0.0
            else:
                outdata[:] = data[:frames]

        def recreate_stream_if_needed(new_index):
            nonlocal output_stream, current_output_index
            if output_stream:
                output_stream.stop()
                output_stream.close()
                output_stream = None
            try:
                output_stream = sd.OutputStream(
                    samplerate=sample_rate,
                    channels=2,
                    dtype='float32',
                    device=new_index,
                    callback=audio_callback,
                    latency='high',
                    blocksize=10200
                )
                print(f'Switched micro output to device index {new_index}')
                current_output_index = new_index
            except Exception as e:
                print(f"Error creating output stream: {e}")
                current_output_index = None
                output_stream = None

        try:
            while True:

                data = conn.recv(16384)
                if not data:
                    break
                
                new_index = runtime_config['micro_output']
                if new_index is not None and new_index != current_output_index:
                    recreate_stream_if_needed(new_index)

                buffer += data

                while len(buffer) >= frame_size * batch_frames:
                    chunk = buffer[:frame_size * batch_frames]
                    buffer = buffer[frame_size * batch_frames:]

                    arr = np.frombuffer(chunk, dtype=np.int32)
                    left = arr[::2]
                    right = arr[1::2]
    
                    sio.emit('micro-signal', {
                        'left': left.tobytes(),
                        'right': right.tobytes(),
                    })

                    stereo = (np.stack([left, right], axis=1) / (2**32)).astype(np.float32)

                    if output_stream:
                        audio_queue.put(stereo)

                        if not warmup_done:
                            total_frames = sum(audio.shape[0] for audio in list(audio_queue.queue))
                            if total_frames >= warmup_target_frames:
                                try:
                                    output_stream.start()
                                    warmup_done = True
                                    print("Warmup done, output stream started")
                                except Exception as e:
                                    print(f"Error starting output stream: {e}")
                                    warmup_done = False

        except Exception as e:
            print(f"Error receiving or sending micro signals: {e}")
        finally:
            if output_stream:
                output_stream.stop()
                output_stream.close()
