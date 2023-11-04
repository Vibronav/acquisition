# vnav-acquisition

Tool for synchronous acquisition of audio (from rasberry_pi/banana_pi devboard)
and video from webcam.

Code to run in Jupyter Notebook:
```commandline
from vnav_acquisition.interface import build_interface
from vnav_acquisition.comm import on_rec_start, on_rec_stop

build_interface()
```