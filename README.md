# Vibronav acquisition tools

Tools for synchronous acquisition of audio (from rasberry_pi/banana_pi devboard) and video from webcam, and signal processing.

## vnav_acquisition

```commandline
usage: vnav_acquisition [-h] [--setup SETUP]

Web browser interface for synchronous acquisition of audio (from
rasberry_pi/banana_pi devboard) and video from webcam

options:
  -h, --help     show this help message and exit
  --setup SETUP  Path to setup JSON file (if not provided or some fields are
                 missing, default configuration is used.)
```

Run in commandline:
```commandline
vnav_acquisition --setup /path/to/setup.json
```
This runs application in Python and opens web interface in web browser. Stop application with Ctrl+C in commandline.
Setup JSON file format:
```
{
    "connection": ["hostname", port_number, "username", "password"], 
    "materials": ["material_1", "material_2"],
    "speeds": ["speed_1", "speed_2", "speed_3"],
    'local_dir': r"c:\vnav_acquisition",
    'remote_dir': "vnav_acquisition"    
}
```

Recordings from microphone(s) are recorded at RasberryPi device in directory `/home/pi/$remote_dir$` 
and downloaded locally to `$local_dir$`. Audio recording is postprocessed to
remove low frequency components and normalize amplitude. Original recording is renamed to extension `.raw.wav`.

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

## vnav_audio_video_sync

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
```

## Installation

Requires Python 3.10. To install tool, run in command line:

```commandline
python -m pip install https://github.com/Vibronav/acquisition/archive/master.zip
```
### Use Vibronav acqusition V2

To install vnav_acquisition package **unstable React version** (without cloning git repo):
```
python -m pip uninstall vnav-acquisition # if you have old version installed
python -m pip install https://github.com/Vibronav/acquisition/archive/vibronav_acquisition_v2.zip # install react version
```


For development,  to clone git repo:
```
git clone https://github.com/Vibronav/acquisition/tree/vibronav_acquisition_v2
```

you can use `run.sh` script to build and run the app 
```
./run.sh #runs the app
```

To see the changes you’ve made in backend  you need to build backend
```
./run.sh -b #builds backend and runs the app
```

To see the changes you’ve made in front_app/ you need to build frontend 
```
./run.sh -f #builds frontend and runs the app
```

```
./run.sh -fb # builds everything
```

You can open the app on http://localhost:5000


Run backend by using `run.sh` script (this will open also an instance of frontend on localhost:5000, but it doesn’t matter):
```
./run.sh
```

Simultaneously run frontend by:
```
cd front_app
npm start #this will run a frontend on localhost:5173
```

Open http://localhost:5173 in your browser. Now when you make any changes to files in front_app/ directory they will be reflected in the browser instantaneously
