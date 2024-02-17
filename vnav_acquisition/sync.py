import json
import numpy as np
import subprocess
import tempfile
import os
from vnav_acquisition.clean import highpass, read_wave
from vnav_acquisition.sound import generate_chirp_signal
import argparse
import glob


def extract_audio_from_video(video_file: str) -> [int, np.ndarray]:
    """EXTRACT AUDIO FILE FROM .WEBM FILE WITH FFMPEG"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        # convert .webm file to .wav file (extract audio from video file)
        tmp_wav_file = os.path.join(tmpdirname, os.path.basename(video_file) + ".wav")
        ffmpeg_command = ['ffmpeg', '-i', video_file, tmp_wav_file]

        # execute FFmpeg from PowerShell
        try:
            subprocess.run(ffmpeg_command, check=True, shell=True)
            fs, x = read_wave(tmp_wav_file)
            os.remove(tmp_wav_file)
            return fs, x
        except subprocess.CalledProcessError as e:
            print(f'Error while executing FFmpeg: {e}')


def argmax_correlation(input_signal, sync_signal):
    filtered_input_signal = highpass(input_signal)
    sync_len = len(sync_signal)

    sqrt_sum_of_squares = np.sqrt(np.convolve(np.square(filtered_input_signal), np.ones(sync_len), mode="valid"))
    correlation = np.correlate(filtered_input_signal, sync_signal)/sqrt_sum_of_squares

    idx_max = np.argmax(np.abs(correlation))
    return idx_max


def find_delay_by_sync(video_file, audio_file, video_channel=0, audio_channel=-1) -> [float, int]:
    """
    Finds a delay between audio and video recordings based on the position of synchronization sound.
    :param video_file: Path of video file.
    :param audio_file: Path of audio file.
    :param audio_channel: Which channel to look for sync wave in audio file.
    :param video_channel: Which channel to look for sync wave in vieo file.
    :return: Audio file delay in seconds, in respect to audio from video file.
    """
    audio_fs, audio_signal = read_wave(audio_file)
    audio_signal = audio_signal[audio_channel, :]
    sync_signal = generate_chirp_signal(sample_rate=audio_fs)
    audio_shift = argmax_correlation(audio_signal, sync_signal)/audio_fs

    video_fs, video_signal = extract_audio_from_video(video_file)
    video_signal = video_signal[video_channel, :]
    if audio_fs != video_fs:
        sync_signal = generate_chirp_signal(sample_rate=video_fs)
    video_shift = argmax_correlation(video_signal, sync_signal)/video_fs

    audio_delay = audio_shift - video_shift
    return audio_delay, audio_fs


def add_audio_annotations(video_file, audio_file, annotation_file):
    with open(annotation_file) as f:
        annotation_set = json.load(f)

    video_annotations = annotation_set.get("video_annotations", annotation_set["annotations"])
    audio_delay, audio_fs = find_delay_by_sync(video_file, audio_file)

    audio_annotations = dict()
    audio_annotations["start_time"] = video_annotations["start_time"] + audio_delay
    audio_annotations["end_time"] = video_annotations["end_time"] + audio_delay
    audio_annotations["start_sample"] = int(audio_annotations["start_time"] * audio_fs)
    audio_annotations["end_sample"] = int(audio_annotations["end_time"] * audio_fs)

    annotation_set["audio_file"] = audio_file
    annotation_set["audio_annotations"] = audio_annotations

    with open(annotation_file, 'w') as f:
        json.dump(annotation_set, f, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Writes audio annotation based on synchronization between audio, "
                                                 "video and video annotations.")
    parser.add_argument("--audio-path", type=str, required=True,
                        help="Path to audio files")
    parser.add_argument("--audio-suffix", type=str, default="",
                        help='Suffix of audio file, compared to video and annotation files (default: "")')
    parser.add_argument("--video-path", type=str, default="", required=False,
                        help="Path to video (webm, mp4) files (default: same as audio files)")
    parser.add_argument("--annotation-path", type=str, default="", required=False,
                        help="Path to annotations files (default: same as audio files)")
    args = parser.parse_args()

    if not args.video_path:
        args.video_path = args.audio_path
    if not args.annotation_path:
        args.annotation_path = args.audio_path

    audio_files = {os.path.splitext(os.path.basename(f))[0].replace(args.audio_suffix, ""): f
                   for f in glob.glob(args.audio_path + os.sep + "*.wav")}
    video_files = {os.path.splitext(os.path.basename(f))[0]: f
                   for f in glob.glob(args.video_path + os.sep + "*.*") if os.path.splitext(f)[1] in (".webm", ".mp4")}
    annotation_files = {os.path.splitext(os.path.basename(f))[0]: f
                        for f in glob.glob(args.annotation_path + os.sep + "*.json")}

    skipped = 0
    for name, audio_file in audio_files.items():
        if name in video_files and name in annotation_files:
            print(f"Processing {name}")
            add_audio_annotations(video_files[name], audio_file, annotation_files[name])
        else:
            skipped += 1
    if skipped:
        print(f"Skipped {skipped} files with missing data file (video or annotations)")


if __name__ == "__main__":
    main()
