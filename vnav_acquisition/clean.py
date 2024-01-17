import argparse
from scipy.io import wavfile
from scipy.signal import filtfilt
import os
import numpy as np
import glob
import tqdm


def read_wave(path):
    sample_rate, x = wavfile.read(path)
    if x.dtype == np.int32:
        x = x / float(2**31-1)
    elif x.dtype == np.int16:
        x = x / float(2**15-1)
    return sample_rate, x


def highpass(x: np.ndarray, offset_samples: int, filter_order=200):
    h = np.ones(filter_order)/filter_order
    h = np.convolve(np.convolve(h, h), h)
    x = x[offset_samples:, :]
    y = np.zeros_like(x)
    for channel in range(x.shape[1]):
        y[:, channel] = x[:, channel] - filtfilt(h, 1, x[:, channel])
        y[:, channel] /= np.max(np.abs(y[:, channel]))
    return y


def write_wave(path, sample_rate, data, dtype=np.int32):
    if dtype == np.int32:
        data = (data * (2 ** 31 - 1)).astype(dtype)
    elif dtype == np.int16:
        data = (data * (2 ** 15 - 1)).astype(dtype)
    wavfile.write(path, sample_rate, data)


def clean_wav(input_file: str, output_path: str, offset: float, wave_word_size=16, backup_dirname="raw_wav"):
    fs, x = read_wave(input_file)
    x_clean = highpass(x, int(offset*fs))
    output_file = os.path.join(output_path, os.path.basename(input_file))
    if os.path.exists(output_file):
        raw_file = output_file[:-len(".wav")] + ".raw.wav"
        os.rename(output_file, raw_file)
    write_wave(output_file, fs, x_clean, {16: np.int16, 32: np.int32}[wave_word_size])
    return [output_file, raw_file]


def main():
    parser = argparse.ArgumentParser(description="Read, clean and save WAV file(s).")
    parser.add_argument("--input-file", type=str, default="", required=False,
                        help="Single input WAV file to process.")
    parser.add_argument("--input-path", type=str, default="", required=False,
                        help="Path with WAV files file to process.")
    parser.add_argument("--offset", type=float, default=0.02, required=False,
                        help="Time offset to skip at the beginning of waveform.")
    parser.add_argument("--wave-word-size", type=int, default=16, required=False,
                        help="Size of word (16 or 32 bits) for saving WAV file.")
    parser.add_argument("--output-path", type=str, default="", required=False,
                        help='Target directory (if not provided, files will be saved on input path and original '
                             'file(s) moved to "original_wav" folder.')

    args = parser.parse_args()

    if args.input_path:
        input_files = glob.glob(os.path.join(args.input_path, "*.wav"))
        if not args.output_path:
            args.output_path = args.input_path
    elif args.input_file:
        input_files = [args.input_file]
        if not args.output_path:
            args.output_path = os.path.dirname(args.input_file)
    else:
        input_files = []

    for input_file in tqdm.tqdm(input_files):
        clean_wav(input_file, args.output_path, args.offset, args.wave_word_size, backup_dirname="original_wav")


if __name__ == "__main__":
    main()
