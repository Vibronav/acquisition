import os
import time
import paramiko
from .sound import play_chirp_signal
from .clean import clean_wav
from .config import config
import logging

MIC_NAME = "dmic_sv"
CHANNEL_FMT = "stereo"
SAMPLING_RATE = 48000

ssh: paramiko.SSHClient = None
file_name = ""

def is_ssh_connected():
    global ssh
    if ssh is not None and ssh.get_transport() and ssh.get_transport().is_active():
        return True
    return False


## I think we shouldn't try except here. If we cannot connect we should pass exception to caller function up to run_automation and we should stop automating
def ssh_connect(hostname, port, username, password):
    global ssh
    try:
        ssh = paramiko.SSHClient()
        paramiko.util.log_to_file('paramiko_debug.log', level=logging.DEBUG)
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
            print(f"SFPT setup upload completed.")
    except Exception as e:
        print(f"SFPT setup upload error.", e)
        ssh = None


def on_rec_start(connection, username, material, speed):
    print("Executing 'on_rec_start': Starting micro on needle")
    global ssh
    global file_name
    file_name = f"{username}_{material}_{speed}_{time.strftime('%Y-%m-%d_%H.%M.%S', time.localtime())}.wav"

    if ssh is None:
        ssh_connect(*connection)
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

