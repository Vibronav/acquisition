import os
import socket
import threading
import queue
import numpy as np
import sounddevice as sd
from .runtime_config import runtime_config

micro_signal_thread = None

FRAMES_PER_PACKET = 512
BYTES_PER_SAMPLE = 4
CHANNELS = 2
BYTES_PER_FRAME = CHANNELS * BYTES_PER_SAMPLE
PACKET_BYTES = FRAMES_PER_PACKET * BYTES_PER_FRAME
BATCH_FRAMES = 25
BATCH_BYTES = BATCH_FRAMES * PACKET_BYTES
SAMPLE_RATE = 48000

def is_listener_thread_running():
    global micro_signal_thread
    return micro_signal_thread is not None and micro_signal_thread.is_alive()

def start_micro_signal_sending():
    print("Starting micro signal sending on RaspberryPi")
    # command = "python3 -u /home/pi/micro_signal_sender.py"
    # ssh.exec_command(command)

    import subprocess, sys
    wav_path = r"C:\Users\jakub\Desktop\ncn\acquisition\1_6_22rpm_turkey_speed-10_shiba_2025-08-07_16.21.20.wav"

    script_path = os.path.join(os.path.dirname(__file__), "micro_signal_sender_file.py")
    args = [
        sys.executable, "-u", script_path,
        "--host", "127.0.0.1",
        "--port", "5001",
        "--wav", wav_path,
    ]

    print("Starting local wav sender:", args)
    subprocess.Popen(args)

def listen_for_micro_signals(sio):
        global micro_signal_thread
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 5001))
        s.listen(1)
        print("Waiting for connection to micro signal server...")
        s.settimeout(10)
        try:
            conn, addr = s.accept()
            print(f"Connection from {addr}")
            micro_signal_thread = threading.Thread(target=receive_and_send_micro_signals, args=(conn, sio,), daemon=True)
            micro_signal_thread.start()
        except socket.timeout:
            print("No connection received within timeout period.")

        print("Finished thread for listening to connection from raspberrypi")

def _make_output_stream(device_index, callback):
    return sd.OutputStream(
        samplerate=SAMPLE_RATE,
        channels=2,
        dtype='float32',
        device=device_index,
        callback=callback,
        latency='high',
        blocksize=FRAMES_PER_PACKET
    )

def receive_and_send_micro_signals(conn, sio):
        
    buffer_audio = bytearray()
    buffer_data = bytearray()
    audio_queue = queue.Queue(maxsize=32)

    current_output_index = None
    output_stream = None
    warmup_state = {"done": False, "target_elements": 18}
    leftover = np.zeros((0, 2), dtype=np.float32)

    def audio_callback(outdata, frames, time_info, status):
        nonlocal leftover

        if not warmup_state["done"]:
            outdata[:] = 0.0
            return
        
        needed = frames
        write_pos = 0

        if leftover.shape[0] > 0:
            take = min(needed, leftover.shape[0])
            outdata[:take, :] = leftover[:take, :]
            write_pos += take
            needed -= take

            if take < leftover.shape[0]:
                leftover = leftover[take:, :]
            else:
                leftover = np.zeros((0, 2), dtype=np.float32)

        while needed > 0:
            try:
                block = audio_queue.get_nowait()
            except queue.Empty:
                print("Audio queue is empty, filling with silence")
                outdata[write_pos:frames, :] = 0.0
                return
            
            if block.shape[0] <= needed:
                outdata[write_pos:write_pos + block.shape[0], :] = block
                write_pos += block.shape[0]
                needed -= block.shape[0]
            else:
                outdata[write_pos:write_pos + needed, :] = block[:needed, :]
                leftover = block[needed:, :]
                write_pos = frames
                needed = 0
                break

        if write_pos < frames:
            print(f'Filling remaining output buffer with silence from {write_pos} to {frames}')
            outdata[write_pos:frames, :] = 0.0

    try:
        while True:
            data = conn.recv(16384)
            if not data:
                break

            new_index = runtime_config['micro_output']
            if new_index is not None and new_index != current_output_index:
                if output_stream:
                    output_stream.stop()
                    output_stream.close()
                    output_stream = None

                try:
                    output_stream = _make_output_stream(new_index, audio_callback)
                    output_stream.start()
                    current_output_index = new_index
                    print(f'Switched micro output to device index: {current_output_index}')
                except Exception as e:
                    print(f"Error switching micro output: {e}")
                    current_output_index = None
                    output_stream = None

            buffer_audio.extend(data)
            buffer_data.extend(data)

            process_audio_sound(buffer_audio, audio_queue, output_stream, warmup_state)
            send_audio_data(buffer_data, sio)

    except Exception as e:
        print(f"Error receiving and sending micro signals: {e}")
    finally:
        if output_stream:
            try:
                output_stream.stop()
                output_stream.close()
            except Exception as e:
                pass

def send_audio_data(buffer, sio):

    while len(buffer) >= BATCH_BYTES:
        batch_bytes = bytes(buffer[:BATCH_BYTES])

        arr = np.frombuffer(batch_bytes, dtype='<i4')
        left = arr[::2]
        right = arr[1::2]

        sio.emit('micro-signal', {
            'left': left.tobytes(),
            'right': right.tobytes()
        })

        del buffer[:BATCH_BYTES]

def process_audio_sound(buffer, audio_queue, output_stream, warmup_state):

    while len(buffer) >= PACKET_BYTES:
        pkt = bytes(buffer[:PACKET_BYTES])
        arr = np.frombuffer(pkt, dtype='<i4').reshape(-1, 2)
        stereo = (arr / (2 ** 31)).astype(np.float32)

        if output_stream:
            try:
                audio_queue.put(stereo, timeout=0.02)
            except queue.Full:
                pass

            print(f'Elements in queue: {audio_queue.qsize()}')

            if not warmup_state["done"]:
                queued_packets = audio_queue.qsize()
                if queued_packets >= warmup_state["target_elements"]:
                    warmup_state["done"] = True
                    print("Warmup done, starting playback")

        del buffer[:PACKET_BYTES]