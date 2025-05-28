

# Dobot Automation

## Prerequisites

* **Python** (3.10+)
* **Git** : For cloning repository

## Instruction

### 1. **Clone or Download**
&nbsp;

**Option A**

===========================================================================
``` bash
git clone https://github.com/Vibronav/acquisition.git
```

After cloning go to the project

``` bash
cd acquisition
```
============================================================================

&nbsp;

**Option B**

===========================================================================

Download ZIP from Github (https://github.com/Vibronav/acquisition.git) and extract

===========================================================================

&nbsp;

**For now after cloning you have to go to VNAV-232 branch, command below**
``` bash
git checkout VNAV-232
```

Then also go to the project folder `acquisition`

&nbsp;

### 2. **Install packages**

When you are in `acquisition` folder

```bash
pip install -r requirements.txt
```

### 3. **Add setup file** (Optional)

Your can add your own setup.json file. Then in next point you can run program with path to this file as parameter

### 4. **Run program**

Without your own setup file:

`python -m vnav_acquisition.webserver --port 5000 --open-browser`

With your file:

`python -m vnav_acquisition.webserver --port 5000 --setup C:\Users\jakub\Desktop\ncn\acquisition\setup.json --open-browser`
