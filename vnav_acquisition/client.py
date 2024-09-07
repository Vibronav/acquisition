import paramiko
import threading
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore

# SSH bağlantısı için gerekli bilgiler
hostname = 'raspberrypi'
port = 22
username = 'pi'
password = 'VibroNav'

CHUNK = 512
RATE = 44100

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

def update_plot():
    app = QtWidgets.QApplication.instance()  # Check if an instance of QApplication exists
    if app is None:
        app = QtWidgets.QApplication([])  # Create a new instance if not
    else:
        app.quit()  # Clean up the old instance if necessary
        app = QtWidgets.QApplication([])

    win = pg.GraphicsLayoutWidget(show=True)
    win.setWindowTitle('Real-time Plot')

    p1 = win.addPlot(title="Left Channel")
    p2 = win.addPlot(title="Right Channel", row=1, col=0)

    curve1 = p1.plot()
    curve2 = p2.plot()

    def plot_update():
        if len(all_data1) > 0 and len(all_data2) > 0:
            min_len = min(len(all_data1), len(all_data2))
            x = np.arange(min_len)
            curve1.setData(x, all_data1[:min_len])
            curve2.setData(x, all_data2[:min_len])

    timer = QtCore.QTimer()
    timer.timeout.connect(plot_update)
    timer.start(50)

    def cleanup():
        timer.stop()
        app.quit()

    win.closeEvent = lambda event: cleanup()

    win.show()
    QtWidgets.QApplication.instance().exec_()

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

if __name__ == "__main__":
    stdout = start_recording()
    threading.Thread(target=data_listener, args=(stdout,), daemon=True).start()
    update_plot()
