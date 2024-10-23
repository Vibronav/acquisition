
# Vibronav Automation Tool - README

This document provides an overview of the Vibronav Automation Tool, its three main components (`automation_interface.py`, `automation_playwright.py`, and `dobot.py`), and instructions for setting up and running the project.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Code Components](#code-components)
3. [User Interface Parameters](#user-interface-parameters)
4. [Automation Workflow](#automation-workflow)
5. [Communication with Dobot](#communication-with-dobot)
6. [Required Libraries](#required-libraries)
7. [Installation and Running Instructions](#installation-and-running-instructions)

---

<a name="project-overview"></a>

## 1. Project Overview

The Vibronav Automation Tool automates a process involving a **Dobot robot arm**, and consists of three main Python scripts:

- **`automation_interface.py`**: The graphical user interface (GUI) that allows the user to input parameters for the automation process.
- **`automation_playwright.py`**: The main automation script, responsible for processing the inputs from the GUI and controlling the automation logic.
- **`dobot.py`**: This script handles communication with the **Dobot robot arm** by sending movement commands based on the automation logic.

These scripts work together to automate tasks by using the Dobot robot arm, with user inputs provided through the GUI.

---

<a name="code-components"></a>

## 2. Code Components

### 1. `automation_interface.py` (User Interface - GUI)
This script creates a **Tkinter-based GUI** where the user can input parameters such as material, speed, position types, and the number of iterations. The user’s input is then passed to `automation_playwright.py` to initiate the automation process.

### 2. `automation_playwright.py` (Main Automation Code)
This is the main automation script that manages the automation sequence. It receives the user’s inputs from `automation_interface.py` and orchestrates the process. It interacts with `dobot.py` to send movement commands to the Dobot robot arm based on the selected parameters.

### 3. `dobot.py` (Dobot Control)
This script communicates with the **Dobot robot arm**, translating the movement commands received from `automation_playwright.py` into actual motions.

---

<a name="user-interface-parameters"></a>

## 3. User Interface Parameters

The following parameters can be set via the user interface in `automation_interface.py`:

1. **Username**: The name of the user running the automation.
2. **Material**: The material to be used in the process (pre-defined in the `setup.json` configuration file).
3. **Speed**: The speed at which the automation will run (also defined in `setup.json`).
4. **Position Type**: Specifies the type of movement for the robot (e.g., "Only Up and Down" or "Up, Down, Forward").
5. **Positions (P1, P2, P3)**: The X, Y, Z coordinates for each position where the robot will move.
6. **Number of Iterations**: The number of times the automation process will repeat.

Once these parameters are entered, pressing the **Submit** button triggers the automation sequence.

---

<a name="automation-workflow"></a>

## 4. Automation Workflow

1. The user provides inputs via the GUI (e.g., material, speed, position type, etc.).
2. The `run_automation()` function in **`automation_playwright.py`** is called with these inputs.
3. This function manages the automation process and communicates with **`dobot.py`** to control the Dobot robot arm’s movements.
4. The robot arm executes the commands based on the specified positions and speed.
5. The process is repeated for the defined number of iterations.

---

<a name="communication-with-dobot"></a>

## 5. Communication with Dobot

The **Dobot robot arm** is controlled through the **`dobot.py`** script, which translates movement instructions into actions. The robot's movements are controlled by receiving position (X, Y, Z) data from `automation_playwright.py` and requires `dobot_api.py` for interfacing with the **Dobot API**, allowing it to perform the task at hand., allowing it to perform the task at hand.

---

<a name="required-libraries"></a>

## 6. Required Libraries

The project uses several Python libraries to handle the user interface, automation logic, and Dobot control. The following libraries are required:

- `tkinter`: For creating the graphical user interface (GUI).
- `ttkthemes`: To add themes to the Tkinter interface.
- `Pillow (PIL)`: For handling images in the GUI.
- `imageio`: For capturing and displaying the camera feed.
- `asyncio`: For managing asynchronous tasks (e.g., real-time camera feed).
- `threading`: For running the camera feed in parallel with the main GUI.
- `functools`: For utility functions like `partial`.
- `playwright`: For automation processes (this may be a custom automation tool integrated into your workflow).

### Installing the Libraries

To install the required dependencies, run the following command in your terminal:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` file should contain the following:

```
ttkthemes
Pillow
imageio
asyncio
playwright
```
### Installing Playwright

After installing the required libraries, you also need to install Playwright dependencies. Run the following command in terminal:

```bash
playwright install
```
This step is crucial to ensure all necessary browser binaries are available for the Playwright library.

### Installing FFmpeg

If FFmpeg is not already installed on your system, you can download and install it by following the instructions specific to your operating system:

- For Windows, download the latest build from FFmpeg's official [https://www.ffmpeg.org/download.html] site and follow the installation instructions.
- For macOS, you can use Homebrew:
```bash
brew install ffmpeg
```
- For Linux, use your package manager, for example:
```bash
sudo apt-get install ffmpeg
```

---

<a name="installation-and-running-instructions"></a>

## 7. Installation and Running Instructions

### 1. Install Python and Required Libraries

Make sure you have **Python 3.8+** installed. Install the required libraries by running:

```bash
pip install -r requirements.txt
```

### 2. Prepare the `setup.json` File and 

You must have a configuration file (`setup.json`) that defines the available materials and speeds. For example:

```json
{
    "connection": ["host", "RPi_port", "RPi_username", "RPi_password"], 
    "materials": ["Slime", "Silicone", "PU", "Plato (play dough)", "Plastic", "Ikea (plastic bag)", "African (silk)"],
    "speeds": ["slow", "medium", "fast"],
    "local_dir": "C:\\vnav_acquisition",
    "remote_dir": "vnav_acquisition"
}
```

Make sure the file is placed in the correct directory as referenced in `automation_interface.py` and also in `automation_playwright.py`
**setup_json_path** `= r'C:\path\to\your\setup.json'`

Additionally, ensure the following directory is set in `automation_playwright.py` for saving records:

**video_output_dir** `= r'C:\path\to\your\output_videos'`

### 3. Running the Application

To start the GUI and begin the automation process, follow these steps:

1. **Start the web server**:
    - Open your terminal and first run the `webserver.py` to start the web server:
    
```bash
    python webserver.py
```
    Now close the program which is opened on web browser. This will run the server in the background without opening a terminal window, and the program will continue running.

2. **Start the GUI**:
    - Then, open another terminal and run the following command to start the GUI and begin the automation process:

```bash
    python automation_interface.py 
```
    or

```bash
    py automation_interface.py 
```

This will open the graphical user interface (GUI) for entering parameters, and the web server will continue running in the background.

### 4. Submitting Parameters

Once the GUI appears:
1. Enter the required parameters (Username, Material, Speed, Position Types, etc.).
2. Click the **Submit** button to start the automation process.

The GUI will also display a **real-time camera feed** during the operation, which runs in a separate thread.

### 5. Customizing Paths

Ensure that the following paths in your code are updated to match your system's configuration:
- **`setup_json_path`** in `automation_interface.py`: Update to match the path of your `setup.json` file.
- **`video_output_dir`**: Ensure this path in `automation_playwright.py` matches your desired video output directory.

Example for updating the paths:

```python
setup_json_path = r'C:\path\to\your\setup.json'
video_output_dir = r'C:\path\to\your\output_videos'
```

### 5. Closing the Program

To safely close the program, return to the terminal where the application is running and press **`Ctrl + C`**. This will terminate the processes without requiring you to close the opened GUI windows directly.

---

### Additional Information

- Ensure that the **Dobot robot arm** is correctly set up and connected to your system.
- All movements are executed based on the position coordinates (P1, P2, P3) provided in the GUI.
- The camera feed updates in real time and provides a visual reference for the automation process.

--- 

This document outlines how to set up and run the Vibronav Automation Tool, providing step-by-step instructions for working with the GUI, running the automation scripts, and communicating with the Dobot robot arm.
