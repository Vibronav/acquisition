import time
from vnav_acquisition.config import config
from vnav_acquisition.comm import on_rec_start, on_rec_stop, kill_rasp_process
from vnav_acquisition.dobot import connect_robot, enable_robot, move_to_position
from .record import start_recording, stop_recording
from .utils import build_filename
    
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


def run_automation(material, needle_type, microphone_type, description, stop_event, initX, finishX, upZ, downZ, speed, motion_type, num_iterations, socketio_instance):
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
    # dashboard, move = connect_robot()
    # enable_robot(dashboard)
    time.sleep(2)

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

    if motion_type == "Up, Down, Forward":
        gap = (finishX - initX) / num_iterations
        print(f"Gap between X positions: {gap}")
    else:
        gap = 0
        print("No gap calculation needed for motion type: Only Up and Down")

    P1 = (initX, 0, upZ, 0)
    P2 = (initX, 0, downZ, 0)

    for i in range(num_iterations):

        if stop_event.is_set():
            print("Stop event triggered. Exiting loop.")
            break

        socketio_instance.emit("iteration", {
            "iteration": i+1
        })

        # move_to_position(dashboard, move, P1)
        print(f'Moving to initial position P1: {P1}')

        output_filename_prefix = build_filename(description, material, speed, needle_type, microphone_type)
        
        is_started = start_recording(output_filename_prefix, socketio_instance)

        if not is_started:
            continue

        time.sleep(0.5)
        print(f"Recording {i+1}/{num_iterations} started.")

        # Move to P2
        # move_to_position(dashboard, move, P2)
        print(f'Moving to position P2: {P2}')
        time.sleep(3)
        
        # Move back to P1
        # move_to_position(dashboard, move, P1)
        print(f'Moving back to initial position P1: {P1}')
        time.sleep(2)
            
        P1 = (P1[0] + gap, P1[1], P1[2], P1[3])
        P2 = (P2[0] + gap, P2[1], P2[2], P2[3])

        print(f'Changed P1 to: {P1}')
        print(f'Changed P2 to: {P2}')

        stop_recording(socketio_instance)

        time.sleep(1)

        print(f"Iteration {i+1} completed.")

    # dashboard.DisableRobot()
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