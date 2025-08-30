import argparse
import os
import subprocess
from .sync import extract_audio_from_video, argmax_correlation, get_stream_start_times
from vnav_acquisition.sound import generate_chirp_signal

def cut_video(video_path, cut_seconds):
    tmp_path = video_path.replace(".mp4", "_shifted.mp4")
    ffmpeg_command = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", video_path,
        "-ss", f'{cut_seconds:.6f}',
        "-map", "0",
        "-c:v", "libx264",
        tmp_path
    ]

    subprocess.run(ffmpeg_command)
    os.replace(tmp_path, video_path)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Tool for synchrozing video to make them start at same time. Tool is cutting videos and override!" \
                    " Tool will synchronize videos with same filename in both folders." \
                    " Video will be cut to start 0.2 seconds before chirp sound. If it is to short, it will be cut to the start of chirp sound."
    )
    parser.add_argument("--first-video-folder", required=True, type=str, help="Path to folder with first video(s).")
    parser.add_argument("--second-video-folder", required=True, type=str, help="Path to folder with second video(s).")
    parser.add_argument("--debug-plots", action='store_true', help="If set, debug plots will be shown.")
    return parser.parse_args()

def main():
    args = parse_args()

    first_video_folder = args.first_video_folder
    second_video_folder = args.second_video_folder
    debug_plots = args.debug_plots

    video_filenames = [f for f in os.listdir(first_video_folder) if f.endswith(".mp4")]

    for video_filename in video_filenames:
        first_video_path = os.path.join(first_video_folder, video_filename)
        second_video_path = os.path.join(second_video_folder, video_filename)

        if not os.path.exists(first_video_path) or not os.path.exists(second_video_path):
            print(f"Missing video file(s) for synchronization: {first_video_path}, {second_video_path}")
            continue

        fs1, signal1 = extract_audio_from_video(first_video_path)
        signal1 = signal1[0, :]
        sync_signal = generate_chirp_signal(sample_rate=fs1)
        audio1_shift = argmax_correlation(signal1, sync_signal, fs1, debug_plots=debug_plots)

        fs2, signal2 = extract_audio_from_video(second_video_path)
        signal2 = signal2[0, :]
        if fs2 != fs1:
            sync_signal = generate_chirp_signal(sample_rate=fs2)
        audio2_shift = argmax_correlation(signal2, sync_signal, fs2, debug_plots=debug_plots)

        v1_start, a1_start = get_stream_start_times(first_video_path)
        v2_start, a2_start = get_stream_start_times(second_video_path)

        video1_shift = (a1_start - v1_start) + (audio1_shift / fs1)
        video2_shift = (a2_start - v2_start) + (audio2_shift / fs2)

        if video1_shift - 0.2 > 0 and video2_shift - 0.2 > 0:
            cut1 = video1_shift - 0.2
            cut2 = video2_shift - 0.2
        else:
            cut1 = video1_shift
            cut2 = video2_shift

        cut_video(first_video_path, cut1)
        cut_video(second_video_path, cut2)

if __name__ == "__main__":
    main()