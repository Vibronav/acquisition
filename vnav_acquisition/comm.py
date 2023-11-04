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
    filename = f'{username}_{material}_{speed}_{time.strftime("%Y-%m-%d_%H.%M.%S", time.localtime())}'
    if ssh:
        stdin, stdout, stderr = ssh.exec_command(f"arecord -D dmic_sv -c2 -r 44100 -f S32_LE -t wav -V mono -v {filename}.wav")
        print(stdout.read().decode('utf-8'))
    time.sleep(delay)
    play_chirp_signal()


def on_rec_stop():
    global ssh
    # ssh.send("\x03")
    pass



