import os
import socket
import threading
import queue
import time
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
PACKET_PERIOD_SEC = FRAMES_PER_PACKET / SAMPLE_RATE

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
        blocksize=128
    )

def clear_queue(audio_queue):
    try:
        while True:
            audio_queue.get_nowait()
    except queue.Empty:
        pass

def start_audio_pacer(buffer_audio, buffer_audio_lock, audio_queue, warmup_state, state):
    stop_event = threading.Event()

    def pacer_run():
        next_t = time.perf_counter()
        while not stop_event.is_set():
            next_t += PACKET_PERIOD_SEC

            with buffer_audio_lock:
                if len(buffer_audio) >= PACKET_BYTES:
                    pkt = bytes(buffer_audio[:PACKET_BYTES])
                    del buffer_audio[:PACKET_BYTES]
                else:
                    pkt = None

            if pkt:
                arr = np.frombuffer(pkt, dtype='<i4').reshape(-1, 2)
                block = (arr / (2 ** 31)).astype(np.float32)

                try:
                    audio_queue.put(block, timeout=0.02)
                except queue.Full:
                    pass

            output_stream = state.get('output_stream')
            if output_stream and not warmup_state["done"]:
                if audio_queue.qsize() >= warmup_state["target_elements"]:
                    try:
                        warmup_state["done"] = True
                        try:
                            print(f"Output stream samplerate: {output_stream.samplerate}")
                        except Exception as e:
                            pass
                        print("Warmup done, starting playback")
                    except Exception as e:
                        print(f"Error starting output stream: {e}")

            rem = next_t - time.perf_counter()
            if rem > 0:
                time.sleep(rem)
            else:
                next_t = time.perf_counter()

    t = threading.Thread(target=pacer_run, daemon=True)
    t.start()
    return t, stop_event

def receive_and_send_micro_signals(conn, sio):

    try:
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except Exception as e:
        pass

    buffer_audio = bytearray()
    buffer_data = bytearray()
    buffer_audio_lock = threading.Lock()

    audio_queue = queue.Queue(maxsize=32)
    warmup_state = {"done": False, "target_elements": 18}
    state = {"output_stream": None}

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
                print("Audio queue is empty, filling with silence. Start warming up")
                outdata[write_pos:frames, :] = 0.0
                warmup_state["done"] = False
                return
            
            if block.shape[0] <= needed:
                outdata[write_pos:write_pos + block.shape[0], :] = block
                write_pos += block.shape[0]
                needed -= block.shape[0]
            else:
                outdata[write_pos:write_pos + needed, :] = block[:needed, :]
                leftover = block[needed:, :]
                return


    current_output_index = None
    output_stream = None
    pacer_thread = None
    pacer_stop = None
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

                warmup_state["done"] = False
                leftover = leftover[:0, :]
                clear_queue(audio_queue)

                try:
                    output_stream = _make_output_stream(new_index, audio_callback)
                    current_output_index = new_index
                    output_stream.start()
                    state["output_stream"] = output_stream
                    print(f'Switched micro output to device index: {current_output_index}')

                except Exception as e:
                    print(f"Error switching micro output: {e}")
                    current_output_index = None
                    output_stream = None
                    state["output_stream"] = None

                if pacer_stop is None or not pacer_thread.is_alive():
                    pacer_thread, pacer_stop = start_audio_pacer(
                        buffer_audio, buffer_audio_lock, audio_queue, warmup_state, state
                    )


            with buffer_audio_lock:
                buffer_audio.extend(data)
            buffer_data.extend(data)

            # process_audio_sound(buffer_audio, audio_queue, output_stream, warmup_state)
            send_audio_data(buffer_data, sio)

    except Exception as e:
        print(f"Error receiving and sending micro signals: {e}")
    finally:
        if pacer_stop:
            pacer_stop.set()
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
