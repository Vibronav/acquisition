import subprocess
import time
import shlex

# Construct the FFmpeg command
ffmpeg_command = (
    'ffmpeg -f dshow -rtbufsize 2000M -t 60 '
    '-i "video=HP HD Camera:audio=Headset (realme Buds Wireless 2 Neo Hands-Free AG Audio)" '
    '-y -vcodec libx264 -crf 24 output.mp4'
)

# Use shlex.split to handle the command as a list of arguments
recorder = subprocess.Popen(shlex.split(ffmpeg_command), stdin=subprocess.PIPE)

# Sleep for the desired recording time (10 seconds)
time.sleep(10)

# Gracefully stop FFmpeg
recorder.stdin.write('q'.encode("GBK"))  # Simulate user pressing 'q'
recorder.stdin.flush()  # Ensure the command is sent
recorder.communicate()  # Wait for the process to finish
recorder.wait()  # Ensure the process has terminated
