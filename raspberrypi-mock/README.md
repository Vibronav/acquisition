# raspberry-pi mock

This direcotry contains code to run a contenerized raspberrypi mock that has access to host's microphone. 

**Disclaimer** :exclamation:
This solution was only tested on MacOS operating system.

### Requirements to run the mock
- Docker installed
- Pulseaudio installed
- Running pulseaudio server. Can be started by using:
``` bash

```

### Running
Inside *raspberrypi-mock* directory run command:
``` bash
docker-compose up -d
```

Log into the raspberrypi mock using:
``` bash
ssh -p 2222 pi@localhost
```
and password *VibroNav*.
