import alsaaudio
import socket
import time

BROADCAST_PORT = 54545

def find_server_ip():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_sock.bind(('', BROADCAST_PORT))

    print("Waiting for broadcast from server...")

    while True:
        try:
            data, addr = udp_sock.recvfrom(1024)
            print(f"Received broadcast from {addr[0]}: {data.decode()}")        
            return addr[0]
        except Exception as e:
            print(f"Error receiving broadcast: {e}")


SERVER_IP = find_server_ip()
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