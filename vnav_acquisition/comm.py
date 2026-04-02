import os
import time
import paramiko
from .config import config
from .live_audio_data import listen_for_micro_signals, start_micro_signal_sending, is_listener_thread_running
from . import microphone
import threading

ssh: paramiko.SSHClient = None
file_name = ""


def is_ssh_connected():
    global ssh
    if ssh is not None and ssh.get_transport() and ssh.get_transport().is_active():
        return True
    return False


def ssh_connect(hostname, port, username, password, socketio_instance):
    global ssh
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

    if config["microphoneType"] == "MEMS":
        if not is_listener_thread_running():
            threading.Thread(target=listen_for_micro_signals, args=(socketio_instance,), daemon=True).start()

        time.sleep(1)
        start_micro_signal_sending(ssh)
    else:
        print(f'Only MEMS microphone is supported for live data')
    

def on_rec_start(connection, socketio_instance, output_filename):
    global ssh, file_name
    
    file_name = output_filename
    microphone_type = config['microphoneType']
    
    if ssh is None:
        ssh_connect(*connection, socketio_instance=socketio_instance)
        time.sleep(1)
    
    if microphone_type == "Contact":
        return microphone.start_contact(ssh, file_name)
    elif microphone_type == "MEMS":
        return microphone.start_mems(ssh, file_name)
    else:
        print(f"Invalid microphone type while starting recording: {microphone_type}")
        return False


def on_rec_stop(delete=False):
    global ssh, file_name

    microphone_type = config['microphoneType']
    if microphone_type == "Contact":
        return microphone.stop_contact(ssh, file_name, delete)
    elif microphone_type == "MEMS":
        return microphone.stop_mems(ssh, file_name, delete)
    else:
        print(f"Invalid microphone type while stopping recording: {microphone_type}")
        return False


def kill_rasp_process():
    """Kill any running MEMS recording process."""
    global ssh
    microphone_type = config['microphoneType']
    if microphone_type == "MEMS":
        microphone.kill_mems_process(ssh)
    elif microphone_type == "Contact":
        microphone.kill_contact_process(ssh)
    else:
        print(f"Invalid microphone type while killing process: {microphone_type}")


def delete_last_recording():
    """Delete the last recorded files locally."""
    global file_name
    deleted = []
    for file in [file_name, file_name[:-len(".wav")] + ".raw.wav"]:
        file_path = os.path.join(config["local_dir"], file)
        if os.path.exists(file_path):
            os.remove(file_path)
            deleted.append(file_path)
            print(file_path, "deleted")
        else:
            print(file_path, "does not exist")
    return deleted
