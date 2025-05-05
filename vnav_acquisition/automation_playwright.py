import os
import time
from playwright.sync_api import sync_playwright
from vnav_acquisition.config import config
import subprocess
from datetime import datetime
from dobot import connect_robot, enable_robot, move_to_position

def start_recording(output_filepath):
    """Starts recording video + audio using ffmpeg via subprocess.Popen."""
    frame_width = 1920
    frame_height = 1080
    fps = 30
    audio_rate = 48000
    video_source = "Jabra PanaCast 20"  
    audio_device_name = "Mikrofon (Jabra PanaCast 20)"  

    command = [
        'ffmpeg',
        '-f', 'dshow',
        '-rtbufsize', '1G',
        '-video_size', f"{frame_width}x{frame_height}",
        '-framerate', str(fps),
        '-i', f"video={video_source}",
        '-f', 'dshow',
        '-i', f"audio={audio_device_name}",
        '-ar', str(audio_rate),
        '-ac', '1',
        '-c:v', 'libx264',
        '-c:a', 'libopus',
        '-b:a', '256k',
        '-preset', 'fast',
        '-filter:a', 'loudnorm',
        '-async', '1',
        '-strict', 'experimental',
        output_filepath
    ]

    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    return process

def stop_recording(process):
    """Stops the ffmpeg recording by sending 'q' to its stdin."""
    if process.stdin:
        process.stdin.write(b'q')
        process.stdin.flush()
        process.wait(timeout=1)
    else:
        print("Error: Process stdin is None")

def get_flask_port():
    """Reads the Flask port number from flask_port.txt (in the same directory)."""
    port_file_path = os.path.join(os.path.dirname(__file__), 'flask_port.txt')
    if os.path.exists(port_file_path):
        with open(port_file_path, 'r') as f:
            return f.read().strip()
    else:
        raise Exception("Flask port file not found.")

def run_automation(username, material, speed=None, position_type=None, p1=None, p2=None, p3=None, num_iterations=None):
    """
    Main automation functions:
      - Launches Playwright, sets up camera/audio,
      - Connects to the Dobot Mg400,
      - Iterates through the given number of loops,
      - Moves the robot and records audio+video, 
      - Adjusts positions after certain iteration counts.
    """
    setup_json_path = r'C:\Users\ucunb\OneDrive\Masaüstü\acquisition-master2\setup.json'
    config.load_from_json(setup_json_path)
    flask_port = get_flask_port()

    video_output_dir = os.path.join(os.path.dirname(setup_json_path), "videos")
    os.makedirs(video_output_dir, exist_ok=True)
    print(f"Video directory verified: {video_output_dir}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            permissions=["camera", "microphone"],
            record_video_dir=video_output_dir,
            record_video_size={"width": 1280, "height": 720}
        )

        page = context.new_page()
        page.goto(f"http://localhost:{flask_port}")
        page.locator('select#videoSource').select_option(index=1)
        page.locator('select#audioSource').select_option(index=1)

        page.fill('input#username', username)
        page.wait_for_selector(f'input[type="radio"][name="material"][value="{material}"]')
        page.locator(f'input[type="radio"][name="material"][value="{material}"]').check()

        if speed is not None:
            page.wait_for_selector(f'input[type="radio"][name="speed"][value="{speed}"]')
            page.locator(f'input[type="radio"][name="speed"][value="{speed}"]').check()

        page.wait_for_timeout(5000)  # Adjust if needed

        # Connect to Dobot
        dashboard, move = connect_robot()
        enable_robot(dashboard)
        time.sleep(2)

        if num_iterations is None:
            num_iterations = 12

        # Map speed string to numeric speed factor
        if speed == "slow":
            speed_value = 10
        elif speed == "medium":
            speed_value = 15
        elif speed == "fast":
            speed_value = 25
        elif speed is None:
            speed_value = 15

        dashboard.SpeedFactor(speed_value)

        # Determine positions
        if position_type == "Only Up and Down":
            P1 = p1
            P2 = None
            P3 = p3
        elif position_type == "Up, Down, Forward":
            P1 = p1
            P2 = p2
            P3 = p3
        else:
            # Default positions if none are given
            P1 = (300, 0, 80, 0) 
            P2 = (P1[0], P1[1], 80, P1[3])
            P3 = (P1[0], P1[1], 0, P1[3])

        for i in range(num_iterations):
            try:
                timestamp = time.strftime('%Y-%m-%d_%H.%M.%S', time.localtime())
                output_filename = f"{username}_{material}_{speed}_{timestamp}.mp4"
                output_filepath = os.path.join(video_output_dir, output_filename)

                move_to_position(dashboard, move, P1)
                time.sleep(1)

                print(f"Recording {i+1}/{num_iterations} started.")
                recording_process = start_recording(output_filepath)

                page.wait_for_selector('button#rec', state='visible')
                page.click('button#rec')
                print("Record button clicked.")

                # Skip actual movement for first 2 iterations, just wait
                if i < 2:
                    print(f"Skipping Dobot movement for iteration {i+1}.")
                    time.sleep(8)  
                else:
                    if P2:
                        move_to_position(dashboard, move, P2)
                        #time.sleep(3)
                        
                    # Move to P3
                    move_to_position(dashboard, move, P3)
                    #time.sleep(3)
                    time.sleep(1)
                    
                    # Move back to P1
                    move_to_position(dashboard, move, P1)
                    #time.sleep(3)
                    

                page.wait_for_selector('button#stop', state='visible')
                page.click('button#stop')
                print("Stop button clicked.")

                if i >= 2:  # Start modifying positions after the 3rd iteration (i == 2)
                    if (i + 1) % 35 == 0:
                        # Increase Y by 3 and reset X to initial value after every n iterations
                        initial_x = 300  # Initial X position
                        P1 = (initial_x, P1[1] + 3, P1[2], P1[3])
                        if P2 is not None:
                            P2 = (initial_x, P2[1] + 3, P2[2], P2[3])
                        P3 = (initial_x, P3[1] + 3, P3[2], P3[3])
                        print(f"Y axis increased by 3 and X reset after 40 iterations. New Y = {P1[1]}, Reset X = {P1[0]}")
                
                    if P2 is not None:
                        # Shift X by 3 every iteration after the 3rd one
                        P1 = (P1[0] + 3, P1[1], P1[2], P1[3])
                        P2 = (P2[0] + 3, P2[1], P2[2], P2[3])
                        P3 = (P3[0] + 3, P3[1], P3[2], P3[3])
                        print(f"X axis increased by 3. New X = {P1[0]}")
                    else:
                        print("P2 not used, only P1 and P3 updated.")

                time.sleep(2.5)
                stop_recording(recording_process)
                if i >= 2:
                    
                    print(f"Iteration {i+1} completed.")

            except Exception as e:
                print(f"An error occurred in iteration {i+1}: {e}")

        dashboard.DisableRobot()
        context.close()
        browser.close()
        print(f"All {num_iterations} loops completed. Browser closed.")

if __name__ == "__main__":
    run_automation(
        username="test_user",
        material=config["materials"][0],
        speed=config["speeds"][1],
        position_type=None,
        p1=None,
        p2=None,
        p3=None,
        num_iterations=None
    ) 