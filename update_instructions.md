To update app to version execute following commands:

Uninstall old version
```commandline
python -m pip uninstall -y vnav_acqiusition
```

This will install the new version of the app:
```commandline
python -m pip install git+https://github.com/Vibronav/acquisition.git@vibronav_acqiusition_v2
```

Or to install **old version** run:
```commandline
python -m pip install git+https://github.com/Vibronav/acquisition.git@master
```
Always run the *uninstall* command inbetween switching the versions.

Run the app with:
```commandline
vnav_acquisition --setup setup.json
```
