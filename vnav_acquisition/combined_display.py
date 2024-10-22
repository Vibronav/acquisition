import cv2
import numpy as np
import threading
import paramiko
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
from collections import deque
import time

# SSH connection details
hostname = 'raspberrypi' 
port = 22
username = 'pi'
password = 'VibroNav'

CHUNK = 512
RATE = 44100
DURATION = 5000  # Duration in seconds (don't write 5 it's not working as we expected)

# Deques to store the last 5 seconds of data
max_length = RATE * DURATION // CHUNK
all_data1 = deque(maxlen=max_length)
all_data2 = deque(maxlen=max_length)

# Global variable to track printed frequencies
last_print_time = 0
current_object = None  # To track the current detected object
stop_event = threading.Event()  # Event to stop threads

# Define frequency thresholds for different objects
frequency_thresholds = {
    "Sponge": (8000, 10500),
    #"Dry Sponge": (9000, 10500),
    "Paper": (2000, 4000),
}

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
    app = QtWidgets.QApplication.instance()
    if app is None:
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
            curve1.setData(x, list(all_data1)[:min_len])
            curve2.setData(x, list(all_data2)[:min_len])

    timer = QtCore.QTimer()
    timer.timeout.connect(plot_update)
    timer.start(50) # Update plot every 50 ms

    def cleanup():
        timer.stop()
        app.quit()

    win.closeEvent = lambda event: cleanup()

    # Check for 'q' key press to stop the application
    def keyPressEvent(event):
        if event.key() == QtCore.Qt.Key_Q:
            stop_event.set()  # Set the stop event
            cleanup()

    win.keyPressEvent = keyPressEvent

    win.show()
    QtWidgets.QApplication.instance().exec_()

def data_listener(stdout):
    global all_data1, all_data2

    while not stop_event.is_set():
        data = stdout.read(CHUNK * 8) 
        if len(data) == CHUNK * 8:  
            data = np.frombuffer(data, dtype=np.int32)
            data1 = data[::2]  # Left channel (needle microphone)
            data2 = data[1::2]  # Right channel (normal microphone)

            all_data1.extend(data1) # Append the new data
            all_data2.extend(data2) # Append the new data

            # Perform frequency analysis
            analyze_frequency(data1, data2) 

def analyze_frequency(data1, data2): 
    global last_print_time, current_object 

    # Remove DC offset, If the average of the audio signals is different from zero, this may cause errors in frequency analysis.
    data1 = data1.copy() - np.mean(data1)  # Create a copy  
    data2 = data2.copy() - np.mean(data2)  # Create a copy 

    # Compute FFT for both channels
    # The frequency components of both channels are calculated with the function. This process converts signals in the time domain to the frequency domain.
    fft_result1 = np.fft.fft(data1)
    fft_result2 = np.fft.fft(data2)

    # Frequency and Amplitude Calculation
    freqs1 = np.fft.fftfreq(len(fft_result1), 1 / RATE) # Frequency values
    freqs2 = np.fft.fftfreq(len(fft_result2), 1 / RATE) # Frequency values
    
    magnitudes1 = np.abs(fft_result1) # Magnitude values
    magnitudes2 = np.abs(fft_result2) # Magnitude values

    # Use only positive frequencies
    positive_freqs1 = freqs1[:len(freqs1) // 2] 
    positive_magnitudes1 = magnitudes1[:len(magnitudes1) // 2] 

    positive_freqs2 = freqs2[:len(freqs2) // 2]
    positive_magnitudes2 = magnitudes2[:len(magnitudes2) // 2]

    # Find the dominant frequencies
    dominant_index1 = np.argmax(positive_magnitudes1)
    dominant_index2 = np.argmax(positive_magnitudes2)

    dominant_freq1 = positive_freqs1[dominant_index1]
    dominant_freq2 = positive_freqs2[dominant_index2]

    current_time = time.time()

    # Check general ambient sounds (0-500 Hz)
    for freq, channel in [(dominant_freq1, 'left'), (dominant_freq2, 'right')]:
        if 0 <= freq <= 500:
            if current_time - last_print_time > 6:  # Check if 6 seconds have passed
                print(f"Sounds coming from the general environment ({channel} channel): {freq:.2f} Hz")
                last_print_time = current_time

    # Check frequency thresholds for both channels
    detected_object1 = check_thresholds(dominant_freq1)
    detected_object2 = check_thresholds(dominant_freq2)

    if detected_object1 != current_object:
        if detected_object1:
            print(f"You are in the {detected_object1.capitalize()} (needle microphone). Frequency: {dominant_freq1:.2f} Hz")
        current_object = detected_object1  # Update current object
    elif detected_object2 != current_object:
        if detected_object2:
            print(f"You are in the {detected_object2.capitalize()} (normal microphone). Frequency: {dominant_freq2:.2f} Hz")
        current_object = detected_object2  # Update current object
    elif detected_object1 is None and detected_object2 is None and current_object is not None:
        print("Nesne algılanmadı.")
        current_object = None  # Reset current object

    # Handle unknown frequencies
    if detected_object1 is None and (dominant_freq1 > 5000 or dominant_freq1 < 0):
        print(f"Unknown frequency (left channel): {dominant_freq1:.2f} Hz")
    #if detected_object2 is None and (dominant_freq2 > 5000 or dominant_freq2 < 0):
        #print(f"Bilinmeyen frekans (sağ kanal): {dominant_freq2:.2f} Hz")


# Check if the dominant frequency is within the thresholds
def check_thresholds(dominant_freq):
    for obj, (low, high) in frequency_thresholds.items():
        if low <= dominant_freq <= high:
            return obj
    return None

def show_camera_feed():
    cap = cv2.VideoCapture(1)  # Camera index 1
    if not cap.isOpened():
        print("Camera index 1 not found.")
        return

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame from camera.")
            break

        # Resize the frame to twice its original size
        frame_resized = cv2.resize(frame, (0, 0), fx=1, fy=1)

        cv2.imshow('Camera Feed', frame_resized)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()  # Set the stop event
            break

    cap.release()
    cv2.destroyAllWindows()

def run_combined_display():
    stdout = start_recording()
    threading.Thread(target=data_listener, args=(stdout,), daemon=True).start()

    camera_thread = threading.Thread(target=show_camera_feed)
    plot_thread = threading.Thread(target=update_plot)

    camera_thread.start()
    plot_thread.start()

    camera_thread.join()
    plot_thread.join()

if __name__ == "__main__":
    run_combined_display()
