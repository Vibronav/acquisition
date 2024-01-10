import os
import time
import paramiko
from .sound import play_chirp_signal
from .config import config

MIC_NAME = "dmic_sv"
CHANNEL_FMT = "stereo"
SAMPLING_RATE = 48000

ssh = None
file_name = ""


def ssh_connect(hostname, port, username, password):
    global ssh
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)
    # cp /home/pi/asoundrc.txt /home/pi/.asoundrc


def on_rec_start(connection, username, material, speed, delay=0.05):
    global ssh
    global file_name
    file_name = f"{username}_{material}_{speed}_{time.strftime('%Y-%m-%d_%H.%M.%S', time.localtime())}.wav"
    if ssh is None:
        ssh_connect(*connection)
        time.sleep(1)
    play_chirp_signal(delay)
    if ssh:
        print("Recording started")
        remote_path = f"{config['remote_dir']}/{file_name}"
        mkdir_commad = f"mkdir {os.path.dirname(remote_path)}"
        ssh.exec_command(mkdir_commad)

        setup_command = f"echo 'DEVICE={MIC_NAME}\nDURATION=10\nSAMPLE_RATE={SAMPLING_RATE}\n" \
                        f"CHANNELS=2\nOUTPUT_FILE={remote_path}\nFORMAT=S32_LE' > " \
                        f"{config['remote_dir']}/recording_setup.txt"
        ssh.exec_command(setup_command)

        start_command = f"bash -c 'source {config['remote_dir']}/recording_setup.txt && nohup arecord " \
                        f"-D $DEVICE -r $SAMPLE_RATE -c $CHANNELS -f $FORMAT -t wav -V {CHANNEL_FMT} " \
                        f"$OUTPUT_FILE &'"
        ssh.exec_command(start_command)
    else:
        print("SSH not connected")
    return os.path.splitext(file_name)[0]


def on_rec_stop(delete=False):
    global ssh
    global file_name
    recording_status = False
    if ssh:
        print("Recording stopped")
        stop_command = f"kill -INT $(ps aux | grep '[a]record -D {MIC_NAME}' | awk '{{print $2}}')"
        ssh.exec_command(stop_command)

        remote_path = f"{config['remote_dir']}/{file_name}"
        local_path = os.path.join(config["local_dir"], file_name)
        os.makedirs(config["local_dir"], exist_ok=True)

        try:
            sftp = ssh.open_sftp()
            sftp.get(remote_path, local_path)
        except:
            print(f"SFPT download error. (remote '{remote_path}', local '{local_path}'.")
        finally:
            sftp.close()
        recording_status = os.path.isfile(local_path) and os.path.getsize(local_path)

        if delete:
            delete_command = f"rm {remote_path}"
            ssh.exec_command(delete_command)
    else:
        print("SSH not connected")
    return recording_status
