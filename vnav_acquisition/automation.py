import json
import os
import time

from vnav_acquisition.config import config
from vnav_acquisition.comm import on_rec_start, on_rec_stop, kill_rasp_process
from vnav_acquisition.dobot import connect_robot, enable_robot, disable_robot, move_to_position

from .record import start_recording, stop_recording
from .utils import build_filename

dashboard = None


def handle_automation_error(socketio_instance, error):
    global dashboard
    print(f'AUTOMATION STOPPED WITH ERROR: {error}')
    kill_rasp_process()
    socketio_instance.emit("automation-status", {
        "status": "idle",
    })
    socketio_instance.emit("record", {
        "action": "stop",
        "shouldUpload": False
    })
    if dashboard:
        disable_robot(dashboard)
    dashboard = None
    
def safe_run_automation(socketio_instance, **kwargs):
    try:
        run_automation(**kwargs, socketio_instance=socketio_instance)
    except Exception as e:
        handle_automation_error(socketio_instance, e)


def run_automation(
        material, 
        needle_type, 
        microphone_type, 
        description, 
        stop_event, 
        initX, 
        finishX, 
        upZ, 
        downZ, 
        y,
        r,
        speed, 
        motion_type, 
        num_iterations, 
        interval, 
        sleep_time, 
        socketio_instance):
    """
    Main automation functions:
      - Connects to the Dobot Mg400,
      - Iterates through the given number of loops,
      - Moves the robot and records audio+video, 
      - Adjusts positions after certain iteration counts.
    """
    global dashboard
    print("Executing 'run_automation'")

    socketio_instance.emit("automation-status", {
        "status": "running",
    })

    dashboard, move = connect_robot()
    enable_robot(dashboard)
    time.sleep(2)

    if motion_type == "Up, Down, Forward":
        gap = (finishX - initX) / num_iterations
        print(f"Gap between X positions: {gap}")
    else:
        gap = 0
        print("No gap calculation needed for motion type: Only Up and Down")

    P1 = (initX, y, upZ, r)
    P2 = (initX, y, downZ, r)

    for i in range(num_iterations):

        if stop_event.is_set():
            print("Stop event triggered. Exiting loop.")
            break

        socketio_instance.emit("iteration", {
            "iteration": i+1
        })

        move_to_position(dashboard, move, P1, speed_l=speed)
        print(f'Moving to initial position P1: {P1}')
        time.sleep(0.3)

        output_filename_prefix = build_filename(description, material, f'Speed-{speed}', needle_type, microphone_type)
        
        is_started = start_recording(output_filename_prefix, socketio_instance)

        if not is_started:
            continue

        time.sleep(0.5)
        print(f"Recording {i+1}/{num_iterations} started.")

        curr_Z = P1[2]

        curr_Z -= interval
        while(curr_Z >= downZ):
            P2 = (P2[0], P2[1], curr_Z, P2[3])
            move_to_position(dashboard, move, P2, speed_l=speed)
            print(f'Moving to position P2: {P2}')
            time.sleep(sleep_time)
            curr_Z -= interval

        curr_Z += (2 * interval)
        while(curr_Z <= upZ and interval != upZ - downZ):
            P2 = (P2[0], P2[1], curr_Z, P2[3])
            move_to_position(dashboard, move, P2, speed_l=speed)
            print(f'Moving to position P2: {P2}')
            curr_Z += interval
            if curr_Z <= upZ:
                time.sleep(sleep_time)
        
        # Move back to P1
        move_to_position(dashboard, move, P1, speed_l=speed)
        print(f'Moving back to initial position P1: {P1}')
        time.sleep(0.5)
            
        P1 = (P1[0] + gap, P1[1], upZ, P1[3])
        P2 = (P2[0] + gap, P2[1], downZ, P2[3])

        print(f'Changed P1 to: {P1}')
        print(f'Changed P2 to: {P2}')

        stop_recording(socketio_instance)

        time.sleep(1)

        print(f"Iteration {i+1} completed.")

    disable_robot(dashboard)
    dashboard = None
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


def safe_run_grid_automation(socketio_instance, **kwargs):
    try:
        run_grid_automation(**kwargs, socketio_instance=socketio_instance)
    except Exception as e:
        handle_automation_error(socketio_instance, e)


def load_grid_config(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Grid config file does not exist: {path}")

    with open(path) as f:
        raw = json.load(f)

    required_keys = ("initial_z", "r", "x_map", "y_map", "z_distance_map")
    for key in required_keys:
        if key not in raw:
            raise ValueError(f"Missing '{key}' in grid config")

    z_distance_map = {}
    for z, distance in raw["z_distance_map"].items():
        z_distance_map[round(float(z), 4)] = str(distance)

    x_rows = []
    for x, row_config in raw["x_map"].items():
        if "row" not in row_config:
            raise ValueError(f"Each X entry must contain 'row'. Problematic X: {x}")

        x_rows.append({
            "x": float(x),
            "row": str(row_config["row"]),
        })

    y_columns = []
    for y, column_config in raw["y_map"].items():
        if "column" not in column_config or "z_values" not in column_config:
            raise ValueError(f"Each Y entry must contain 'column' and 'z_values'. Problematic Y: {y}")

        z_values = [round(float(z), 4) for z in column_config["z_values"]]
        if not z_values:
            raise ValueError(f"Missing z_values for Y={y}")

        for idx in range(1, len(z_values)):
            if z_values[idx] >= z_values[idx - 1]:
                raise ValueError(f"z_values for Y={y} must go down from the first value to the last value")

        for z in z_values:
            if z not in z_distance_map:
                raise ValueError(f"Missing distance label for Z={z}")

        y_columns.append({
            "y": float(y),
            "column": str(column_config["column"]),
            "z_values": z_values,
        })

    if not x_rows:
        raise ValueError("Grid config must contain at least one X row")
    if not y_columns:
        raise ValueError("Grid config must contain at least one Y column")

    initial_z = float(raw["initial_z"])
    max_grid_z = max(z for column in y_columns for z in column["z_values"])
    if initial_z <= max_grid_z:
        raise ValueError("initial_z must be higher than every measurement Z")

    return {
        "initial_z": initial_z,
        "r": float(raw["r"]),
        "z_distance_map": z_distance_map,
        "x_rows": x_rows,
        "y_columns": y_columns,
    }


def grid_point_name(column, row, z, z_distance_map):
    return f"{column}{row}_{z_distance_map[round(float(z), 4)]}"


def grid_safe_position(x, y, grid_config):
    return (x, y, grid_config["initial_z"], grid_config["r"])


def grid_point_position(x, y, z, grid_config):
    return (x, y, z, grid_config["r"])


def count_grid_points(grid_config):
    z_count = sum(len(column["z_values"]) for column in grid_config["y_columns"])
    return z_count * len(grid_config["x_rows"])


def run_grid_automation(
        material,
        needle_type,
        microphone_type,
        description,
        stop_event,
        grid_config_path,
        speed,
        sleep_time,
        socketio_instance):
    """
    Grid automation:
      - Reads robot coordinates from a JSON file,
      - Moves only in XY at the safe initial Z height,
      - Disables the robot at every measurement point,
      - Records audio+video using the same recording flow as the existing automation.
    """
    global dashboard
    print("Executing 'run_grid_automation'")

    grid_config = load_grid_config(grid_config_path)
    total_points = count_grid_points(grid_config)
    completed = 0

    socketio_instance.emit("automation-status", {
        "status": "running",
    })

    dashboard, move = connect_robot()
    enable_robot(dashboard)
    time.sleep(2)

    should_stop = False
    for column_config in grid_config["y_columns"]:
        y = column_config["y"]
        column = column_config["column"]

        for row_config in grid_config["x_rows"]:
            if stop_event.is_set():
                should_stop = True
                break

            x = row_config["x"]
            row = row_config["row"]
            safe_position = grid_safe_position(x, y, grid_config)

            print(f"\n=== Row {row}, column {column}: X={x}, Y={y} ===")
            move_to_position(
                dashboard,
                move,
                safe_position,
                speed_l=speed
            )

            for z in column_config["z_values"]:
                if stop_event.is_set():
                    should_stop = True
                    break

                point_name = grid_point_name(column, row, z, grid_config["z_distance_map"])
                socketio_instance.emit("iteration", {
                    "iteration": completed + 1,
                    "total": total_points,
                    "label": point_name,
                })

                point_position = grid_point_position(x, y, z, grid_config)
                print(f"Moving to grid point {point_name}: {point_position}")
                move_to_position(
                    dashboard,
                    move,
                    point_position,
                    speed_l=speed
                )

                disable_robot(dashboard)

                output_filename_prefix = build_filename(
                    point_name,
                    description,
                    material,
                    f'Speed-{speed}',
                    needle_type,
                    microphone_type
                )

                is_started = start_recording(output_filename_prefix, socketio_instance)
                if is_started:
                    print(f"Recording started for {point_name}.")
                    time.sleep(sleep_time)
                    stop_recording(socketio_instance)
                    print(f"Recording stopped for {point_name}.")
                else:
                    print(f"Recording could not be started for {point_name}.")

                completed += 1
                enable_robot(dashboard)

                if stop_event.is_set():
                    should_stop = True
                    break

            move_to_position(
                dashboard,
                move,
                safe_position,
                speed_l=speed
            )

            if should_stop:
                break

        if should_stop:
            break

    print(f"Grid automation completed: {completed}/{total_points} point(s)")

    disable_robot(dashboard)
    dashboard = None
    socketio_instance.emit("automation-status", {
        "status": "idle",
    })
