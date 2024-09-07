from flask import Flask, render_template, Response
import cv2
import threading
import paramiko
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore

app = Flask(__name__)

# Kamera verilerini işleme
camera_indices = [1, 2]  # Kullanmak istediğiniz kamera indeksleri
caps = [cv2.VideoCapture(i) for i in camera_indices]

def generate_frames():
    while True:
        for cap in caps:
            ret, frame = cap.read()
            if not ret:
                continue
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Ses verisi için SSH bağlantısı ve veri işleme
hostname = 'raspberrypi'
port = 22
username = 'pi'
password = 'VibroNav'

CHUNK = 512
all_data1 = np.array([], dtype=np.int32)
all_data2 = np.array([], dtype=np.int32)

def ssh_command(command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port, username, password)
    stdin, stdout, stderr = client.exec_command(command)
    return stdout

def start_recording():
    command = "python3 -u /home/pi/berke/server.py"
    return ssh_command(command)

def data_listener(stdout):
    global all_data1, all_data2
    while True:
        data = stdout.read(CHUNK * 8)
        if len(data) == CHUNK * 8:
            data = np.frombuffer(data, dtype=np.int32)
            data1 = data[::2]
            data2 = data[1::2]
            all_data1 = np.append(all_data1, data1)
            all_data2 = np.append(all_data2, data2)

@app.route('/')
def index():
    return render_template('index2.html')

def run_sound_processing():
    stdout = start_recording()
    threading.Thread(target=data_listener, args=(stdout,), daemon=True).start()

# Flask uygulaması başlatıldığında
if __name__ == '__main__':
    run_sound_processing()
    app.run(host='0.0.0.0', port=5000, debug=True)
