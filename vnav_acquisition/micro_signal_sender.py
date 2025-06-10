import alsaaudio
import socket
import time

IP_FILE = "home/pi/pc_ip.txt"

def read_server_ip():
    try:
        with open(IP_FILE, "r") as f:
            return f.read().strip()
    except IOError as e:
        print(f"Error reading IP file: {e}")
        return None

SERVER_IP = read_server_ip()
PORT = 5001
CHUNK = 512
RATE = 48000
CHANNELS = 2

mic = alsaaudio.PCM(
    type=alsaaudio.PCM_CAPTURE, mode=alsaaudio.PCM_NORMAL,
    device='dmic_sv_shared', channels=CHANNELS, rate=RATE,
    format=alsaaudio.PCM_FORMAT_S32_LE, periodsize=CHUNK
)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, PORT))

try:
    while True:
        l, data = mic.read()
        if l:
            sock.sendall(data)
        else:
            time.sleep(0.01)
except KeyboardInterrupt:
    print("Stopping stream")
finally:
    sock.close()