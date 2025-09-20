# micro_signal_sender_file.py
import argparse
import socket
import time
import numpy as np
import soundfile as sf

RATE_REQUIRED = 48000
CHANNELS_REQ = 2
PACKET_FRAMES = 512
BYTES_PER_FRAME = CHANNELS_REQ * 4  # stereo * int32
PACKET_BYTES = PACKET_FRAMES * BYTES_PER_FRAME
PERIOD = PACKET_FRAMES / RATE_REQUIRED  # ~0.010666...

# --- Windows: podbij rozdzielczość timera, żeby nie utknąć na 15.6 ms ---
def _win_timer_high_res(enable=True):
    try:
        import ctypes
        if enable:
            ctypes.windll.winmm.timeBeginPeriod(1)
        else:
            ctypes.windll.winmm.timeEndPeriod(1)
    except Exception:
        pass

def to_s32le_stereo(data_np: np.ndarray) -> np.ndarray:
    """
    Przyjmuje audio w kształcie (N, ch) w float32/int16/int32, zwraca int32 little-endian
    w układzie interleaved stereo (N*2,).
    """
    if data_np.dtype == np.float32:
        x = np.clip(data_np, -1.0, 1.0)
        x = (x * (2**31 - 1)).astype('<i4')
    elif data_np.dtype == np.int16:
        x = (data_np.astype('<i4') << 16)
    elif data_np.dtype == np.int32:
        x = data_np.astype('<i4')
    else:
        # fallback: rzut na float
        x = data_np.astype(np.float32)
        x = np.clip(x, -1.0, 1.0)
        x = (x * (2**31 - 1)).astype('<i4')

    # wymuś stereo (L->L,R->R; mono -> duplikacja)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    elif x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    else:
        x = x[:, :2]
    return x.reshape(-1)  # interleave

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True)
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--wav", required=True)
    args = ap.parse_args()

    # 1) Wczytaj WAV
    data, sr = sf.read(args.wav, always_2d=True)
    print(f"Loaded wav file: {args.wav}, Sample Rate: {sr}, Data Shape: {data.shape}")
    if sr != RATE_REQUIRED:
        raise ValueError(f"WAV ma {sr} Hz; wymagane {RATE_REQUIRED} Hz (zrób resampling).")

    # 2) Konwersja do S32_LE interleaved stereo -> bytes
    s32_interleaved = to_s32le_stereo(data)
    if (s32_interleaved.size % 2) != 0:
        s32_interleaved = s32_interleaved[:-1]
    payload = s32_interleaved.astype('<i4').tobytes()
    N = len(payload)

    # 3) TCP i precyzyjny pacing 512 @ 48k
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.connect((args.host, args.port))
    print(f"Połączono z {args.host}:{args.port}. Start streamu z pliku: {args.wav}")

    _win_timer_high_res(True)
    try:
        idx = 0
        next_t = time.perf_counter()

        while True:
            if idx + PACKET_BYTES > N:
                # zapętl palik dla wygody testów
                idx = 0

            chunk = memoryview(payload)[idx:idx + PACKET_BYTES]
            sock.sendall(chunk)
            idx += PACKET_BYTES

            # celuj w dokładnie 10.666… ms na pakiet
            next_t += PERIOD
            while True:
                now = time.perf_counter()
                rem = next_t - now
                if rem <= 0:
                    break
                # duży zapas -> krótki sleep, minimalny zapas -> krótki spin
                if rem > 0.002:
                    time.sleep(0.001)
                else:
                    # krótki spin bez sleep (omija 15.6ms kwantum)
                    pass

    except KeyboardInterrupt:
        pass
    finally:
        _win_timer_high_res(False)
        sock.close()

if __name__ == "__main__":
    main()