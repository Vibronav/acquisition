import os
import time
from playwright.sync_api import sync_playwright
from vnav_acquisition.config import config
from vnav_acquisition.comm import on_rec_start, on_rec_stop, kill_rasp_process
from vnav_acquisition.dobot import connect_robot, enable_robot, move_to_position
import socketio

def get_flask_port():
    """Reads the Flask port number from flask_port.txt (in the same directory)."""
    port_file_path = os.path.join(os.path.dirname(__file__), 'flask_port.txt')
    if os.path.exists(port_file_path):
        with open(port_file_path, 'r') as f:
            return f.read().strip()
    else:
        raise Exception("Flask port file not found.")
    
def safe_run_automation(**kwargs):
    """
    Wrapper function to run the automation, handle any exception and proceed actions that is needed when automation stopped working
    """
    try:
        run_automation(**kwargs)
    except Exception as e:
        print(f'AUTOMATION STOPPED WITH ERROR: {e}')
        kill_rasp_process()
        sio = socketio.Client()
        sio.sleep(1)
        sio.connect(f'http://localhost:5000', wait_timeout=2)
        sio.sleep(1)
        sio.emit("automation-status", {
            "status": "idle",
        })
        sio.emit("record", {
            "action": "stop",
            "shouldUpload": False
        })


def run_automation(username, material, stop_event, speed=None, position_type=None, p1=None, p2=None, p3=None, num_iterations=None, audio_device=None, video_device=None):
    """
    Main automation functions:
      - Launches Playwright, sets up camera/audio,
      - Connects to the Dobot Mg400,
      - Iterates through the given number of loops,
      - Moves the robot and records audio+video, 
      - Adjusts positions after certain iteration counts.
    """
    print("Executing 'run_automation'")
    setup_json_path = r'C:\Users\ucunb\OneDrive\Masaüstü\acquisition-master2\setup.json'
    # config.load_from_json(setup_json_path)
    flask_port = get_flask_port()
    print('BEGENNING AUTOMATION')

    sio = socketio.Client()
    sio.sleep(1)
    sio.connect(f'http://localhost:5000', wait_timeout=2)
    sio.sleep(1)
    sio.emit("automation-status", {
        "status": "running",
    })

    video_output_dir = os.path.join(os.getcwd(), "videos")
    print(f"Video directory verified: {video_output_dir}")
    os.makedirs(video_output_dir, exist_ok=True)

    with sync_playwright() as p:

        # Connect to Dobot
        # dashboard, move = connect_robot()
        # enable_robot(dashboard)
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

        # dashboard.SpeedFactor(speed_value)

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

            if stop_event.is_set():
                print("Stop event triggered. Exiting loop.")
                break

            sio.emit("iteration", {
                "iteration": i+1
            })

            timestamp = time.strftime('%Y-%m-%d_%H.%M.%S', time.localtime())
            output_filename = f"{username}_{material}_{speed}_{timestamp}.mp4"
            output_filepath = os.path.join(video_output_dir, output_filename)

            # move_to_position(dashboard, move, P1)
            time.sleep(1)

            print(f"Recording {i+1}/{num_iterations} started.")
            
            sio.emit("record", {
                "action": "start",
                "filename": output_filename
            })

            is_started = on_rec_start(config['connection'], username, material, speed)
            if not is_started:
                sio.emit("record", {
                    "action": "stop",
                    "shouldUpload": False
                })
                continue

            # Skip actual movement for first 2 iterations, just wait
            if i < 2:
                print(f"Skipping Dobot movement for iteration {i+1}.")
                time.sleep(8)  
            else:
                if P2:
                    pass
                    # move_to_position(dashboard, move, P2)
                    #time.sleep(3)
                    
                # Move to P3
                # move_to_position(dashboard, move, P3)
                #time.sleep(3)
                time.sleep(1)
                
                # Move back to P1
                # move_to_position(dashboard, move, P1)
                #time.sleep(3)
                

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

            is_recorded = on_rec_stop()
            if not is_recorded:
                sio.emit("record", {
                    "action": "stop",
                    "shouldUpload": False
                })
            else:
                time.sleep(2.5)
                sio.emit("record", {
                    "action": "stop",
                    "shouldUpload": True
                })

            if i >= 2:
                print(f"Iteration {i+1} completed.")

        # dashboard.DisableRobot()
        sio.emit("automation-status", {
            "status": "idle",
        })
        print(f"Tests completed.")

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