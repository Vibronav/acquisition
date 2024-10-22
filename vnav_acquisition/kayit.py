import subprocess
import os
import threading
import signal
import keyboard  # Importing the keyboard library

# Global variables
audio_process = None
video_process = None
stop_requested = False  # Flag to signal when to stop recording

# Video ve ses ayarları
frame_width = 1920
frame_height = 1080

def record_audio(audio_device: str, output_audio_file: str):
    """Records audio and saves it to a temporary WAV file."""
    global audio_process
    ffmpeg_command = [
        'ffmpeg',
        '-f', 'dshow',  # DirectShow for Windows
        '-i', f'audio={audio_device}',  # Audio device
        '-ac', '1',  # Mono audio
        '-ar', '48000',  # Sample rate
        '-b:a', '320k',  # Ses bit oranını arttır
        '-filter:a', 'volume=2.0',  # Increase volume (2.0 means double the original)
        '-y',  # Overwrite output file
        output_audio_file  # Temporary audio file
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Recording audio from: {audio_device}")
        print(f"Audio recorded: {output_audio_file}")
    except subprocess.CalledProcessError as e:
        print(f'FFmpeg audio recording error: {e}')

def record_video(video_device: str, output_video_file: str):
    """Records video and saves it to a temporary MP4 file."""
    global video_process
    ffmpeg_command = [
        'ffmpeg',
        '-f', 'dshow',  # DirectShow for Windows
        '-rtbufsize', '1G',  # Real-time buffer size
        '-video_size', f"{frame_width}x{frame_height}",
        '-i', f'video={video_device}',  # Video device
        '-c:v', 'libx264',  # Video codec (NVIDIA NVENC)
        '-movflags', 'faststart',  # Ensure moov atom is at the beginning
        '-y',  # Overwrite output file
        output_video_file  # Temporary video file
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Recording video from: {video_device}")
        print(f"Video recorded: {output_video_file}")
    except subprocess.CalledProcessError as e:
        print(f'FFmpeg video recording error: {e}')

def merge_audio_video(audio_file: str, video_file: str, output_file: str):
    """Merges audio and video files to produce the final output."""
    ffmpeg_command = [
        'ffmpeg',
        '-i', video_file,  # Video file
        '-i', audio_file,  # Audio file
        '-c:v', 'copy',  # Copy video codec
        '-c:a', 'aac',  # Audio codec (AAC)
        '-strict', 'experimental',  # Required for AAC
        '-y',  # Overwrite output file
        output_file  # Final output file
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Merged audio and video: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f'FFmpeg merging error: {e}')

def stop_recording():
    """Stops both audio and video recording."""
    global audio_process, video_process
    if audio_process:
        audio_process.send_signal(signal.SIGTERM)  # Stop audio recording
    if video_process:
        video_process.send_signal(signal.SIGTERM)  # Stop video recording
    print("Audio and video recording stopped.")

def check_for_stop_signal():
    """Thread to check for 'q' key press to stop recording."""
    global stop_requested
    keyboard.wait('q')  # Wait for 'q' key press
    stop_requested = True  # Set flag to stop recording

def main():
    video_device = "Jabra PanaCast 20"  # Video device
    audio_device = "Mikrofon (Jabra PanaCast 20)"  # Audio device
    output_combined_file = "output_combined.mp4"  # Final output file

    # Creating temporary files
    temp_audio_file = os.path.join(os.getcwd(), "temp_a.wav")
    temp_video_file = os.path.join(os.getcwd(), "temp_v.mp4")

    # Start recording audio and video in separate threads
    audio_thread = threading.Thread(target=record_audio, args=(audio_device, temp_audio_file))
    video_thread = threading.Thread(target=record_video, args=(video_device, temp_video_file))
    
    audio_thread.start()
    video_thread.start()

    # Start the thread for checking user input
    input_thread = threading.Thread(target=check_for_stop_signal)
    input_thread.start()

    # Wait for input thread to finish
    input_thread.join()
    
    stop_recording()

    # Wait for audio and video threads to finish
    audio_thread.join()
    video_thread.join()

    # Check if both audio and video files exist and are not empty
    if os.path.exists(temp_audio_file) and os.path.getsize(temp_audio_file) > 0 and \
       os.path.exists(temp_video_file) and os.path.getsize(temp_video_file) > 0:
        print(f"Audio file size: {os.path.getsize(temp_audio_file)} bytes")
        print(f"Video file size: {os.path.getsize(temp_video_file)} bytes")
        # Merge audio and video files
        merge_audio_video(temp_audio_file, temp_video_file, output_combined_file)
    else:
        print("One of the files is missing or empty, merging skipped.")

    # Remove temporary files
    if os.path.exists(temp_audio_file):
        os.remove(temp_audio_file)
    if os.path.exists(temp_video_file):
        os.remove(temp_video_file)
    print(f"Temporary files deleted: {temp_audio_file}, {temp_video_file}")

if __name__ == "__main__":
    main()