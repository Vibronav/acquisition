# vnav-acquisition

Tool for synchronous acquisition of audio (from rasberry_pi/banana_pi devboard)
and video from webcam.

## Running as web application

Run in commandline:
```commandline
vnav_acquisition
```
This runs application in Python and opens web interface in web browser.

## Running in Jupyter Notebook

Run in Jupyter Notebook cell:
```commandline
from vnav_acquisition.interface import build_interface
from vnav_acquisition.comm import on_rec_start, on_rec_stop

build_interface()
```