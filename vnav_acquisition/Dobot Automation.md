# Dobot Automation — Playwright Runner

A command‑line and scriptable tool to orchestrate Dobot motion recording, browser-based capture, and audio/video synchronization using Playwright and FFmpeg.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Download & Setup](#download--setup)
3. [Install Python Dependencies](#install-python-dependencies)
4. [Configure Scripts](#configure-scripts)
5. [Install Playwright Browsers](#install-playwright-browsers)
6. [Adjust Video & Camera Settings](#adjust-video--camera-settings)
7. [Run the GUI](#run-the-gui)

---

## Prerequisites

* **FFmpeg** (≥4.x): for audio/video capture. Must be installed and added to your system **PATH**.
* **Python** (3.8+)
* **Git**: to clone the repository.

---

## Download & Setup

1. **Clone or Download** the repo as ZIP:

   ```bash
   # Option A: Clone via Git
   ```

git clone [https://github.com/Vibronav/acquisition.git](https://github.com/Vibronav/acquisition.git)

# Option B: Download ZIP from GitHub and extract

````
2. **Enter** the root folder:
```bash
cd acquisition
````

---

## Install Python Dependencies

1. **Navigate** to the `vnav_acquisition` subfolder:

   ```bash
   cd vnav_acquisition
   ```
2. **Install** via requirements:

   ```bash
   pip install -r requirements.txt
   ```

---

## Configure Scripts

These settings must be updated in **both** files:

* `automation_interface.py`
* `automation_playwright.py`

Open each file and find the line defining `setup_json_path`, then update the path to your local `setup.json`. For example:

```
setup_json_path = r'C:/full/yourpath/to/acquisition/setup.json'
```

## Install Playwright Browsers

From the root directory:

```bash
playwright install
```

This installs Chromium, Firefox, and WebKit for Playwright automation.

---

## Run the GUI

1. **Open** a **new** terminal session.
2. **Launch** the interface:

   ```bash
   python automation_interface.py
   ```
3. **Fill in** your parameters (username, material, speed, positions, iterations).
4. **Click** **Submit** — the automation sequence will:

   1. Trigger `automation_playwright.py` via Playwright.
   2. Command the Dobot to move between positions.
   3. Record synchronized audio & video for each iteration.

---

*For troubleshooting:*

* Ensure FFmpeg is callable from any path.
* Verify your `flask_port.txt` is updated by `webserver.py`.
* Match camera/audio device names exactly.
* Inspect logs printed to each terminal for errors.

*Happy automating!*
