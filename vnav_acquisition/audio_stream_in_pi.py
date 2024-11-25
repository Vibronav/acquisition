import alsaaudio
import numpy as np
import sys
import time
import os

CHANNELS = 2     # Stereo for 2 channels
RATE = 44100     # Sampling rate
CHUNK = 1024     # Buffer size for reading

# Configure I2S microphone for stereo capture
try:
    i2s_mic = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE, mode=alsaaudio.PCM_NORMAL,
                            device='hw:1,0', channels=CHANNELS, rate=RATE,
                            format=alsaaudio.PCM_FORMAT_S32_LE, periodsize=CHUNK)
except alsaaudio.ALSAAudioError as e:
    print(f"Error initializing audio device: {e}")
    sys.exit(1)

while True:
    try:
        # Capture audio data
        l, data = i2s_mic.read()

        if l > 0:
            # Split stereo data into left and right channels
            data = np.frombuffer(data, dtype=np.int32)
            data1 = data[::2]  # Left channel
            data2 = data[1::2]  # Right channel

            # Combine and send to output
            combined_data = np.column_stack((data1, data2)).flatten()
            os.write(sys.stdout.fileno(), combined_data.tobytes())
            sys.stdout.flush()

        else:
            # In case of a temporary error, wait briefly before retrying
            time.sleep(0.001)

    except alsaaudio.ALSAAudioError as e:
        print(f"Audio read error: {e}")
        time.sleep(0.1)  # Pause before retrying

    except KeyboardInterrupt:
        print("Streaming stopped by user")
        break
        




