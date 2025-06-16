import time
from vnav_acquisition.config import config
from vnav_acquisition.comm import on_rec_start, on_rec_stop, kill_rasp_process
from vnav_acquisition.dobot import connect_robot, enable_robot, move_to_position
from .record import start_recording, stop_recording
    
def safe_run_automation(socketio_instance, **kwargs):
    """
    Wrapper function to run the automation, handle any exception and proceed actions that is needed when automation stopped working
    """
    try:
        run_automation(**kwargs, socketio_instance=socketio_instance)
    except Exception as e:
        print(f'AUTOMATION STOPPED WITH ERROR: {e}')
        kill_rasp_process()
        socketio_instance.emit("automation-status", {
            "status": "idle",
        })
        socketio_instance.emit("record", {
            "action": "stop",
            "shouldUpload": False
        })


def run_automation(username, material, stop_event, speed=None, motion_type=None, p1=None, p2=None, p3=None, num_iterations=None, socketio_instance=None):
    """
    Main automation functions:
      - Connects to the Dobot Mg400,
      - Iterates through the given number of loops,
      - Moves the robot and records audio+video, 
      - Adjusts positions after certain iteration counts.
    """
    print("Executing 'run_automation'")

    socketio_instance.emit("automation-status", {
        "status": "running",
    })

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
    if motion_type == "Only Up and Down":
        P1 = p1
        P2 = None
        P3 = p3
    elif motion_type == "Up, Down, Forward":
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

        socketio_instance.emit("iteration", {
            "iteration": i+1
        })

        timestamp = time.strftime('%Y-%m-%d_%H.%M.%S', time.localtime())
        output_filename = f"{username}_{material}_{speed}_{timestamp}"

        move_to_position(dashboard, move, P1)
        time.sleep(1)

        print(f"Recording {i+1}/{num_iterations} started.")
        
        is_started = start_recording(output_filename, socketio_instance)

        if not is_started:
            continue

        # Skip actual movement for first 2 iterations, just wait
        if i < 2:
            print(f"Skipping Dobot movement for iteration {i+1}.")
            time.sleep(8)  
        else:
            if P2:
                pass
                move_to_position(dashboard, move, P2)
                time.sleep(3)
                
            # Move to P3
            move_to_position(dashboard, move, P3)
            time.sleep(3)
            
            # Move back to P1
            move_to_position(dashboard, move, P1)
            time.sleep(3)
            

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

        stop_recording(socketio_instance)

        if i >= 2:
            print(f"Iteration {i+1} completed.")

    dashboard.DisableRobot()
    socketio_instance.emit("automation-status", {
        "status": "idle",
    })
    print(f"Tests completed.")

if __name__ == "__main__":
    run_automation(
        username="test_user",
        material=config["materials"][0],
        speed=config["speeds"][1],
        motion_type=None,
        p1=None,
        p2=None,
        p3=None,
        num_iterations=None
    ) 