import argparse
import array
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import wave


BYTES_PER_SAMPLE = 4
DEFAULT_CHANNELS = 2
DEFAULT_DEVICE = "dmic_sv_shared"
DEFAULT_FORMAT = "S32_LE"
DEFAULT_SAMPLE_RATE = 48000
DC_SAMPLE_FRACTION = 0.10
INT32_MIN = -(2 ** 31)
INT32_MAX = (2 ** 31) - 1


def _paths(remote_dir):
    base = Path(remote_dir)
    return {
        "raw": base / "mems_continuous.raw",
        "pid": base / "mems_continuous.pid",
        "trim_pid": base / "mems_continuous_trim.pid",
        "recording_lock": base / "mems_continuous.recording",
        "log": base / "mems_continuous.log",
    }


def _pid_is_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _read_live_pid(pid_path):
    try:
        pid = int(pid_path.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None

    if _pid_is_alive(pid):
        return pid

    try:
        pid_path.unlink()
    except FileNotFoundError:
        pass
    return None


def start(args):
    paths = _paths(args.remote_dir)
    paths["raw"].parent.mkdir(parents=True, exist_ok=True)

    pid = _read_live_pid(paths["pid"])
    if pid is None:
        raw_file = paths["raw"].open("ab", buffering=0)
        log_file = paths["log"].open("ab", buffering=0)
        proc = subprocess.Popen(
            [
                "arecord",
                "-D",
                args.device,
                "-r",
                str(args.sample_rate),
                "-c",
                str(args.channels),
                "-f",
                args.format,
                "-t",
                "raw",
                "-q",
            ],
            stdin=subprocess.DEVNULL,
            stdout=raw_file,
            stderr=log_file,
            start_new_session=True,
            close_fds=True,
        )
        time.sleep(0.2)
        if proc.poll() is not None:
            return proc.returncode or 1

        paths["pid"].write_text(str(proc.pid))
        pid = proc.pid

    trim_pid = _read_live_pid(paths["trim_pid"])
    if trim_pid is None:
        trim_proc = subprocess.Popen(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "trim-loop",
                "--remote-dir",
                args.remote_dir,
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True,
        )
        paths["trim_pid"].write_text(str(trim_proc.pid))

    print(pid)
    return 0


def begin_recording(args):
    paths = _paths(args.remote_dir)
    paths["recording_lock"].write_text(str(time.time()))
    return 0


def end_recording(args):
    paths = _paths(args.remote_dir)
    try:
        paths["recording_lock"].unlink()
    except FileNotFoundError:
        pass
    return 0


def trim_loop(args):
    paths = _paths(args.remote_dir)
    while True:
        if not paths["recording_lock"].exists():
            try:
                with paths["raw"].open("ab") as raw_file:
                    if not paths["recording_lock"].exists():
                        raw_file.truncate(0)
            except FileNotFoundError:
                pass
        time.sleep(1)


def mark(args):
    paths = _paths(args.remote_dir)
    frame_size = args.channels * BYTES_PER_SAMPLE
    size = paths["raw"].stat().st_size if paths["raw"].exists() else 0
    print(size - (size % frame_size))
    return 0


def _clip_int32(value):
    return max(INT32_MIN, min(INT32_MAX, value))


def _remove_dc_offset(samples, channels):
    total_frames = len(samples) // channels
    if total_frames == 0:
        return

    dc_frames = max(1, int(total_frames * DC_SAMPLE_FRACTION))
    frame_step = total_frames / dc_frames
    offsets = []
    for channel in range(channels):
        channel_sum = 0
        for sample_index in range(dc_frames):
            frame = min(total_frames - 1, int(sample_index * frame_step))
            channel_sum += samples[(frame * channels) + channel]
        offsets.append(int(round(channel_sum / dc_frames)))

    for index, value in enumerate(samples):
        samples[index] = _clip_int32(value - offsets[index % channels])


def _remove_dc_offset_numpy(raw, channels):
    try:
        import numpy as np
    except ImportError:
        return None

    samples = np.frombuffer(raw, dtype="<i4").copy()
    frames = samples.reshape((-1, channels))
    dc_frames = max(1, int(len(frames) * DC_SAMPLE_FRACTION))
    indices = np.linspace(0, len(frames) - 1, dc_frames, dtype=np.int64)
    offsets = np.rint(frames[indices].mean(axis=0)).astype(np.int64)
    corrected = frames.astype(np.int64) - offsets
    np.clip(corrected, INT32_MIN, INT32_MAX, out=corrected)
    return corrected.astype("<i4", copy=False).tobytes()


def _read_raw_segment(raw_path, start_byte, end_byte, frame_size):
    start_byte = start_byte - (start_byte % frame_size)
    end_byte = end_byte - (end_byte % frame_size)

    if end_byte <= start_byte:
        return b""

    with raw_path.open("rb") as raw_file:
        raw_file.seek(start_byte)
        raw = raw_file.read(end_byte - start_byte)

    usable_len = len(raw) - (len(raw) % frame_size)
    return raw[:usable_len]


def _save_raw_to_wav(raw, args):
    wav_bytes = _remove_dc_offset_numpy(raw, args.channels)

    if wav_bytes is None:
        samples = array.array("i")
        samples.frombytes(raw)
        if samples.itemsize != BYTES_PER_SAMPLE:
            raise RuntimeError("Platform int size is not 32-bit")
        if sys.byteorder != "little":
            samples.byteswap()

        _remove_dc_offset(samples, args.channels)
        if sys.byteorder != "little":
            samples.byteswap()
        wav_bytes = samples.tobytes()

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(args.channels)
        wav_file.setsampwidth(BYTES_PER_SAMPLE)
        wav_file.setframerate(args.sample_rate)
        wav_file.writeframes(wav_bytes)


def save(args):
    paths = _paths(args.remote_dir)
    frame_size = args.channels * BYTES_PER_SAMPLE
    raw = _read_raw_segment(paths["raw"], args.start_byte, args.end_byte, frame_size)
    if not raw:
        return 2

    _save_raw_to_wav(raw, args)
    return 0


def stop(args):
    paths = _paths(args.remote_dir)
    trim_pid = _read_live_pid(paths["trim_pid"])
    if trim_pid is not None:
        os.kill(trim_pid, signal.SIGTERM)
        try:
            paths["trim_pid"].unlink()
        except FileNotFoundError:
            pass

    end_recording(args)

    pid = _read_live_pid(paths["pid"])
    if pid is None:
        return 0

    os.kill(pid, signal.SIGINT)
    for _ in range(20):
        if not _pid_is_alive(pid):
            break
        time.sleep(0.1)

    if _pid_is_alive(pid):
        os.kill(pid, signal.SIGTERM)

    try:
        paths["pid"].unlink()
    except FileNotFoundError:
        pass
    return 0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("start", "begin-recording", "end-recording", "trim-loop", "mark", "save", "stop"))
    parser.add_argument("--remote-dir", required=True)
    parser.add_argument("--device", default=DEFAULT_DEVICE)
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_SAMPLE_RATE)
    parser.add_argument("--channels", type=int, default=DEFAULT_CHANNELS)
    parser.add_argument("--format", default=DEFAULT_FORMAT)
    parser.add_argument("--start-byte", type=int, default=0)
    parser.add_argument("--end-byte", type=int, default=0)
    parser.add_argument("--output-file", default="")
    return parser.parse_args()


def main():
    args = parse_args()
    return {
        "start": start,
        "begin-recording": begin_recording,
        "end-recording": end_recording,
        "trim-loop": trim_loop,
        "mark": mark,
        "save": save,
        "stop": stop,
    }[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
