import paramiko
import time
from .sound import play_chirp_signal

ssh = None


def ssh_connect(hostname, port, username, password):
    global ssh
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)


def on_rec_start(username, material, speed, delay=0.05):
    global ssh
    play_chirp_signal(delay)
    filename = f'{username}_{material}_{speed}_{time.strftime("%Y-%m-%d_%H.%M.%S", time.localtime())}'
    if ssh:
        stdin, stdout, stderr = ssh.exec_command(
            f"arecord -D dmic_sv -c2 -r 44100 -f S32_LE -t wav -V mono -v vnav_acquisition/{filename}.wav")


def on_rec_stop():
    global ssh
    if ssh:
        ssh.send("\x03")



