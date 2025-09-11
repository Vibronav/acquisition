# Vibronav acquisition tools

Tools for synchronous acquisition of audio (from rasberry_pi/banana_pi devboard) and video from webcam, and signal processing.

## vnav_acquisition

```commandline
usage: vnav_acquisition --setup SETUP [-h] [--port number]

Web browser interface for synchronous acquisition of audio (from
rasberry_pi/banana_pi devboard) and video from webcam

options:
  -h, --help     show this help message and exit
  --setup SETUP  Path to setup JSON file. This is required.
  --port number        Number of port attached to app. (Optional)
```

Run in commandline:
```commandline
vnav_acquisition --setup /path/to/setup.json
```
This runs application in Python and opens web interface in web browser. Stop application with Ctrl+C in commandline.
Full setup JSON file format:
```
{
    "connection": ["hostname", port_number, "username", "password"], 
    "materials": ["material_1", "material_2"],
    "needleTypes": ["Type1", "Type2", "Type3"],
    "microphoneTypes": ["TypeA", "TypeB", "TypeC"],
    "local_dir": r"c:\vnav_acquisition",
    "remote_dir": "vnav_acquisition"
}
```

Recordings from microphone(s) are recorded at RasberryPi device in directory `/home/pi/$remote_dir$` 
and downloaded locally to `$local_dir$`. Audio recording is postprocessed to
remove low frequency components and normalize amplitude. Original recording is renamed to extension `.raw.wav`.

Hostname in connection need to be specified as Ip address of raspberrypi. To get this IP connect to raspberry with e.g. Putty and run command ifconfig. IP should be in the bottom like `192.168.0.110`.

## vnav_wav_process

```
usage: vnav_wav_process [-h] [--input-file INPUT_FILE] [--input-path INPUT_PATH] [--offset OFFSET] [--wave-word-size WAVE_WORD_SIZE] [--output-path OUTPUT_PATH]

Read, clean and save WAV file(s).

options:
  -h, --help            show this help message and exit
  --input-file INPUT_FILE
                        Single input WAV file to process.
  --input-path INPUT_PATH
                        Path with WAV files file to process.
  --offset OFFSET       Time offset to skip at the beginning of waveform.
  --wave-word-size WAVE_WORD_SIZE
                        Size of word (16 or 32 bits) for saving WAV file.
  --output-path OUTPUT_PATH
                        Target directory (if not provided, files will be saved on input path and original file(s) moved to "original_wav" folder.

```

## vnav_audio_video_sync (deprecated)

```
usage: vnav_audio_video_sync [-h] --audio-path AUDIO_PATH
                             [--audio-suffix AUDIO_SUFFIX]
                             [--video-path VIDEO_PATH]
                             [--annotation-path ANNOTATION_PATH]

Writes audio annotation based on synchronization between audio and video, and
video annotations.

options:
  -h, --help            show this help message and exit
  --audio-path AUDIO_PATH
                        Path to audio files
  --audio-suffix AUDIO_SUFFIX
                        Suffix of audio file, compared to video and annotation
                        files (default: "")
  --video-path VIDEO_PATH
                        Path to video (webm, mp4) files (default: same as
                        audio files)
  --annotation-path ANNOTATION_PATH
                        Path to annotations files (default: same as audio
                        files)
  --needle-position-path NEEDLE_POSITION_PATH
                        Path to needle position files If not provided needle position files will not be processed
  --audio-channel AUDIO_CHANNEL
                        Index of channel in WAV audio file to use for sync (e.g. 0=left, 1=right, -1=last). Default: -1
  --debug-plots         Show debug plots for synchronization
```

## vnav_audio_video_sync_new

```
usage: sync_new.py [-h]
                   --audio-path AUDIO_PATH 
                   --first-video-path FIRST_VIDEO_PATH 
                   --second-video-path SECOND_VIDEO_PATH 
                   [--audio-channel AUDIO_CHANNEL] 
                   [--debug-plots]

Cut video files to start at the same time as audio files.

options:
  -h, --help            show this help message and exit
  --audio-path AUDIO_PATH
                        Path to audio files
  --first-video-path FIRST_VIDEO_PATH
                        Path to video (mp4) files
  --second-video-path SECOND_VIDEO_PATH
                        Path to video (mp4) files
  --audio-channel AUDIO_CHANNEL
                        Index of channel in WAV audio file to use for sync (e.g. 0=left, 1=right, -1=last). Default: -1
  --debug-plots         Show debug plots for synchronization
```

## vnav_annotate_positions
```
usage: vnav_annotate_positions --video-path VIDEO_FOLDER_PATH (--cube | --no-cube) [--recursive] [--display]

Tool for annotating position of needle in videos. Can be used to annotate videos in specified folder
or to annotate videos in every subfolder of specified folder (useful for autonomuos annotating all dataset).
For each processed video folder, an output folder named 'labelled_positions' will be created at the same level
as the folder containing the videos. In recursive mode , multiple such output folders will be created.
When you provide distances.txt file in the video folder, it will produce annotations to folder 'annotations'.
distances.txt file should look like: 12,8.5,7,5.4

options:
  -h, --help            show this help message and exit
  --video-path VIDEO_PATH
                        Path to folder with videos
  --marker-length MARKER_LENGTH
                        Length of the Aruco marker in cm (From protocol)
  --marker-margin MARKER_MARGIN
                        Margin around the Aruco marker in cm (From protocol)
  --recursive           Flag to run recursively in subfolders of video-path (good for annotating all videos in dataset)
  --fps FPS             Frames per second for video processing (default: 30)
  --display             If true will display tracker on video
  --cube                If provided will use cube to detect table grund
  --no-cube             If provided will NOT use cube to detect table grund
  --dobot               Argument need to be provided if dobot is used during recordings
  --no-dobot            Argument need to be provided if dobot is NOT used during recordings
  --needle-offset NEEDLE_OFFSET
                        Needle offset in cm (From protocol)
  --z-offset Z_OFFSET   Z-axis offset in cm, if not provided default offset will be used
  --starting-position STARTING_POSITION
                        Starting position of the needle in cm (default: 0.0 cm). Used only by mode without cube
  --table-offset TABLE_OFFSET
                        E.g. when provided 2cm, level 0 will be 2 cm above table (By default 0.0 cm)

```

## vnav_video_video_sync
```
usage: vnav_video_video_sync [-h] --first-video-folder FIRST_VIDEO_FOLDER --second-video-folder SECOND_VIDEO_FOLDER [--debug-plots]

Tool for synchrozing video to make them start at same time. Tool is cutting videos and override! Tool will synchronize videos with same filename in both folders. Video will be cut to start 0.2 seconds before chirp  
sound. If it is to short, it will be cut to the start of chirp sound.

options:
  -h, --help            show this help message and exit
  --first-video-folder FIRST_VIDEO_FOLDER
                        Path to folder with first video(s).
  --second-video-folder SECOND_VIDEO_FOLDER
                        Path to folder with second video(s).
  --debug-plots         If set, debug plots will be shown.
```


## Installation

### Highly recommended instalation

Requires Python 3.10. and ffmpeg 4.3.1 To install tool, run in command line:

1. create folder for tool and enter it
2. open commandline in this folder, then type command to create environment:
```commandline
python -m venv .acq
```

3. Enter envorinment

On windows:
Can be required:
```commandline
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
Then:
```commandline
.acq/Scripts/Activate.ps1
```

On linux:
```commandline
source .acq/bin/activate
```

4. Then for both operating systems to install tool:

```commandline
python -m pip install https://github.com/Vibronav/acquisition/archive/master.zip
```
Or if you want specific version:
```commandline
python -m pip install https://github.com/Vibronav/acquisition/archive/refs/tags/<version>.zip
```

Then to run it you need to open terminal in folder with tool and enter environment as above

### Basic instalation (not recommended)

```commandline
python -m pip install https://github.com/Vibronav/acquisition/archive/master.zip
```
