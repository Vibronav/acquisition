import json
import numpy as np
import subprocess
import tempfile
import os
from vnav_acquisition.clean import highpass, read_wave
from vnav_acquisition.sound import generate_chirp_signal
import argparse
import glob
from collections import defaultdict


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
    inf = np.isinf(correlation)
    nan = np.isnan(correlation)
    if any(inf):
        correlation[np.isinf(correlation)] = 0
        print("Inf corrected")
    if any(nan):
        if sum(nan) > len(filtered_input_signal)//10:
            return None
        else:
            correlation[nan] = 0
            print("NaN corrected")
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
    audio_shift = argmax_correlation(audio_signal, sync_signal)

    video_fs, video_signal = extract_audio_from_video(video_file)
    video_signal = video_signal[video_channel, :]
    if audio_fs != video_fs:
        sync_signal = generate_chirp_signal(sample_rate=video_fs)
    video_shift = argmax_correlation(video_signal, sync_signal)

    if None in [audio_shift, video_shift]:
        return video_shift, audio_shift
    else:
        audio_delay = audio_shift/audio_fs - video_shift/video_fs
        return audio_delay, audio_fs


def add_audio_annotations(video_file, audio_file, annotation_file):
    with open(annotation_file) as f:
        annotation_set = json.load(f)
    if "audio_annotations" in annotation_set:
        return f"'audio_annotations' already present in : {annotation_file}"

    audio_delay, audio_fs = find_delay_by_sync(video_file, audio_file)

    if audio_delay is None:
        return f"Video file sound corrupted: {video_file}"
    if audio_fs is None:
        return f"Audio file sound corrupted: {audio_file}"

    audio_annotations = list()
    video_annotations = annotation_set["video_annotations"]
    if type(video_annotations) is list:
        # interval annotations
        for video_annotation in video_annotations:
            audio_annotation = dict()
            audio_annotation["start_time"] = video_annotation["start_time"] + audio_delay
            audio_annotation["end_time"] = video_annotation["end_time"] + audio_delay
            audio_annotation["start_sample"] = int(audio_annotation["start_time"] * audio_fs)
            audio_annotation["end_sample"] = int(audio_annotation["end_time"] * audio_fs)
            audio_annotations.append(audio_annotation)
    elif type(video_annotations) is dict:
        # event annotations
        audio_annotations = defaultdict(dict)
        for event, video_annotation in video_annotations.items():
            audio_annotations[event]["time"] = video_annotation["time"] + audio_delay
            audio_annotations[event]["sample"] = int(audio_annotations[event]["time"] * audio_fs)
    else:
        raise Exception("Unknown annotation format")

    annotation_set["audio_file"] = os.path.basename(audio_file)
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

    skipped = []
    for name, annotation_file in annotation_files.items():
        audio_present = name in audio_files
        video_present = name in video_files
        if audio_present and video_present:
            print(f"Processing {name}")
            result = add_audio_annotations(video_files[name], audio_files[name], annotation_file)
            if result:
                print(result)
                skipped.append(result)
        else:
            if not audio_present:
                result = f"Missing audio for: {name}"
                print(result)
                skipped.append(result)
            if not video_present:
                result = f"Missing video for: {name}"
                print(result)
                skipped.append(result)
    if skipped:
        print(f"Skipped {len(skipped)} files with missing data file (video or annotations)")
        with open(os.path.join(args.annotation_path, "log.txt"), 'w') as fp:
            fp.writelines([line + "\n" for line in skipped])


if __name__ == "__main__":
    main()
