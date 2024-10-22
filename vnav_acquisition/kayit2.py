import os
import subprocess
from datetime import datetime

# Jabra PanaCast 20 device names
video_source = "Jabra PanaCast 20"  # Video device name
audio_device_name = "Mikrofon (Jabra PanaCast 20)"  # Audio device name

# Video and audio settings
frame_width = 1920
frame_height = 1080
fps = 30
audio_rate = 48000
record_seconds = 8  # Record duration in seconds

# Output directory
video_output_dir = r"C:\Users\ucunb.DESKTOP-JEKP035.000\OneDrive\Masaüstü\acquisition-master2\videos"

def record_audio_video(output_filename, duration):
    # Set the file path
    output_filepath = os.path.join(video_output_dir, output_filename)
    
    command = [
        'ffmpeg',
        '-f', 'dshow',  
        '-rtbufsize', '1G',  
        '-video_size', f"{frame_width}x{frame_height}",
        '-r', str(fps),  # Use -r for frame rate adjustment
        '-i', f"video={video_source}",  
        '-f', 'dshow',  
        '-i', f"audio={audio_device_name}",  
        '-ar', str(audio_rate),
        '-ac', '1',  
        '-t', str(duration),
        '-c:v', 'libx264',  
        '-c:a', 'libopus',  # Audio codec
        '-b:a', '190k',  # High-quality audio bitrate
        '-preset', 'fast',
        '-filter:a', 'loudnorm',  # Optional: Normalize audio
        '-async', '1',  # Synchronize audio with video
        '-strict', 'experimental',  
        output_filepath
    ]

    print(f"Recording audio and video: {output_filepath}")
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"Recording completed: {output_filepath}")
    except subprocess.CalledProcessError as e:
        print(f"Error while executing FFmpeg: {e}")

if __name__ == "__main__":
    # Generate a timestamped filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    output_filename = f"test_{timestamp}.mp4"
    record_audio_video(output_filename, record_seconds)