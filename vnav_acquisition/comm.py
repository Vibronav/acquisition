import os
import time
import paramiko
from .sound import play_chirp_signal
from .clean import clean_wav
from .config import config

MIC_NAME = "dmic_sv"
CHANNEL_FMT = "stereo"
SAMPLING_RATE = 48000

ssh: paramiko.SSHClient = None
file_name = ""


def ssh_connect(hostname, port, username, password):
    global ssh
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)

    try:
        with ssh.open_sftp() as sftp:
            sftp.put(os.path.join(os.path.dirname(__file__), "asoundrc.txt"), "/home/pi/.asoundrc")
            print(f"SFPT setup upload completed.")
    except Exception as e:
        print(f"SFPT setup upload error.", e)


def on_rec_start(connection, username, material, speed):
    global ssh
    global file_name
    file_name = f"{username}_{material}_{speed}_{time.strftime('%Y-%m-%d_%H.%M.%S', time.localtime())}.wav"

    if ssh is None:
        print("Connecting to RaspberryPi with SSH")
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
        print("Setup command: \n", setup_command)
        ssh.exec_command(setup_command)
        time.sleep(0.01)

        start_command = f"bash -c 'source {config['remote_dir']}/recording_setup.txt && nohup arecord " \
                        f"-D $DEVICE -r $SAMPLE_RATE -c $CHANNELS -f $FORMAT -t wav -V {CHANNEL_FMT} " \
                        f"$OUTPUT_FILE &'"
        print("Start command: \n", start_command)
        ssh.exec_command(start_command)
        play_chirp_signal()
    else:
        print("SSH connection failed.")
    return os.path.splitext(file_name)[0]


def on_rec_stop(delete=False):
    global ssh
    global file_name
    recorded_files = []
    if ssh is not None:
        print("Recording stopped")
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
        print("SSH not connected")
    return recorded_files


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

