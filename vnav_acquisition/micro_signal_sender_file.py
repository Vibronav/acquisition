import socket
import time
import wave
import numpy as np
import argparse
import os

BROADCAST_PORT = 54545
PORT = 5001
CHUNK = 512
RATE = 48000
CHANNELS = 2
BYTES_PER_SAMPLE = 4   # S32_LE
FRAME_BYTES = CHANNELS * BYTES_PER_SAMPLE
SLEEP_SEC_PER_CHUNK = CHUNK / RATE

def load_wav_info(path):
    wf = wave.open(path, 'rb')
    sr = wf.getframerate()
    ch = wf.getnchannels()
    sw = wf.getsampwidth()
    return wf, sr, ch, sw

def convert_to_s32le_stereo(raw_bytes, sampwidth, in_channels):
    """Konwersja z int16/int24/int32, mono/stereo -> int32 stereo (S32_LE)"""
    if sampwidth == 2:
        arr = np.frombuffer(raw_bytes, dtype='<i2').astype(np.int32)
        arr = (arr.astype(np.int32) << 16)
    elif sampwidth == 3:
        b = np.frombuffer(raw_bytes, dtype=np.uint8).reshape(-1, 3)
        sign = (b[:, 2] & 0x80) != 0
        i32 = (b[:,0].astype(np.int32) |
               (b[:,1].astype(np.int32) << 8) |
               (b[:,2].astype(np.int32) << 16))
        i32[sign] -= (1 << 24)
        arr = (i32 << 8).astype(np.int32)
    elif sampwidth == 4:
        arr = np.frombuffer(raw_bytes, dtype='<i4')
    else:
        raise ValueError(f"Nieobsługiwany sampwidth={sampwidth}")

    if in_channels == 1:
        arr = np.repeat(arr, 2)
    elif in_channels == 2:
        pass
    else:
        arr = arr.reshape(-1, in_channels)[:, :2].reshape(-1)

    if arr.size % 2 != 0:
        arr = arr[:-1]
    return arr.astype('<i4').tobytes()

def stream_wav(host, port, wav_path, loop=True):
    if not os.path.exists(wav_path):
        raise FileNotFoundError(wav_path)

    wf, sr, ch, sw = load_wav_info(wav_path)
    if sr != RATE:
        wf.close()
        raise ValueError(f"Plik ma {sr} Hz, a wymagane jest {RATE} Hz. Zrób resampling przed użyciem.")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"Połączono z {host}:{port}. Start streamu z pliku: {wav_path}")
    try:
        while True:
            frames_bytes = wf.readframes(CHUNK)
            if len(frames_bytes) == 0:
                if loop:
                    wf.rewind()
                    continue
                else:
                    break

            read_frames = len(frames_bytes) // (sw * ch)
            if read_frames < CHUNK:
                pad = (CHUNK - read_frames) * (sw * ch)
                frames_bytes += b'\x00' * pad

            payload = convert_to_s32le_stereo(frames_bytes, sw, ch)

            start = time.perf_counter()
            sock.sendall(payload)
            spent = time.perf_counter() - start
            to_sleep = SLEEP_SEC_PER_CHUNK - spent
            if to_sleep > 0:
                time.sleep(to_sleep)
    except KeyboardInterrupt:
        print("Przerwano (Ctrl+C).")
    finally:
        wf.close()
        sock.close()
        print("Zamknięto połączenie.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--wav", required=True, help="Ścieżka do pliku WAV (48kHz).")
    ap.add_argument("--no-loop", action="store_true", help="Nie zapętlaj pliku po końcu.")
    args = ap.parse_args()
    stream_wav(args.host, args.port, args.wav, loop=not args.no_loop)
