# vnav-acquisition

Tool for synchronous acquisition of audio (from rasberry_pi/banana_pi devboard)
and video from webcam.

Run in commandline:
```commandline
vnav_acquisition --setup /path/to/setup.json
```
This runs application in Python and opens web interface in web browser.

Setup JSON file format:
```
{
    "connection": ["hostname", port, "username", "password"], 
    "materials": ["material_1", "material_2"],
    "speeds": ["speed_1", "speed_2", "speed_3"],
    'local_dir': r"c:\vnav_acquisition",
    'remote_dir': "vnav_acquisition"    
}
```

Recordings from microphone(s) are recorded at RasberryPi device in directory `/home/pi/$remote_dir$` and downloaded locally to `$local_dir$`.