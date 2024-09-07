import sys
import pyaudio
import numpy as np
from PyQt5 import QtWidgets, QtCore, uic
import pyqtgraph as pg

class AudioRecorder(QtCore.QThread):
    data_signal = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, rate=44100, chunk=1024, format=pyaudio.paInt16, channels=1):
        super().__init__()
        self.rate = rate
        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.running = True

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk)

        while self.running:
            data = stream.read(self.chunk)
            audio_data = np.frombuffer(data, dtype=np.int16)
            self.data_signal.emit(audio_data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        self.running = False

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.recorder = AudioRecorder()
        self.recorder.data_signal.connect(self.update_plot)
        self.recorder.start()

        self.x = np.arange(1024)
        self.y = np.zeros(1024)

    def initUI(self):
        self.setWindowTitle('Real-time Audio Signal')
        self.graphWidget = pg.PlotWidget(self)
        self.setCentralWidget(self.graphWidget)
        self.graphWidget.setYRange(-32768, 32767)
        self.show()

    def update_plot(self, audio_data):
        self.y = np.roll(self.y, -len(audio_data))
        self.y[-len(audio_data):] = audio_data
        self.graphWidget.plot(self.x, self.y, clear=True)

    def closeEvent(self, event):
        self.recorder.stop()
        self.recorder.wait()
        event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
