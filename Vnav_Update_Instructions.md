# Vibronav Data Acquisition App
#### New Version Installation Instructions
It is possible to switch between previous and new version of the app.

To remove previous installation run in terminal / powershell: 
```bash
python -m pip -y uninstall vnav_acquisition
```

To install **new version** run:
```bash
python -m pip install git+https://github.com/Vibronav/acquisition.git@deploy-python
```

Or to install **old version** run:
```bash
pip install pip install git+https://github.com/Vibronav/acquisition.git@master
```
Always run the *uninstall* command inbetween switching the versions.

Run the app with:
```
vnav_acquisition
```


🔴 In the new version preview from multiple cameras in available, however recording is only possible when one camera is selected. 
