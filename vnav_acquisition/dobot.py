import time
import os
from dobot_api import DobotApiDashboard, DobotApiMove
from openpyxl import Workbook

# ---------------------------------------------
# Robot IP and Port settings
# ---------------------------------------------
ROBOT_IP = "192.168.1.6"
DASHBOARD_PORT = 29999
MOVE_PORT = 30003
FEED_PORT = 30004 

# ---------------------------------------------
# axis (X, Y, Z, R)
# ---------------------------------------------
P_UP   = (300, 0, 100, 0)  # start (Z=100)
P_DOWN = (300, 0,   0, 0)  # End (Z=0)

# ---------------------------------------------
# 3 diffrent (SpeedFactor)
# ---------------------------------------------
SPEED_LIST = [
    ("Slow(10%)",    50),
    ("Medium(15%)",  50),
    ("Fast(25%)",    50),
]

PARAMS = 0  # 0: No parameters, 1: With parameters

# 
EXCEL_FILENAME = "RobotHareketZamanlari.xlsx"


# ---------------------------------------------
def parse_pose(response):
    """
    Parses the output of Dobot's GetPose() and returns a list [X, Y, Z, R, ...].
    Example response: 'GetPose({300.0, 0.0, 100.0, 0.0, ...})'
    """
    try:
        pose_data = response.split("{")[1].split("}")[0]
        pose_values = [float(val) for val in pose_data.split(",")]
        return pose_values  # [X, Y, Z, R, ...]
    except Exception as e:
        print(f"Error (pose parse): {e}")
        return None

def connect_robot():
    try:
        print("Connecting to the robot...")
        dashboard = DobotApiDashboard(ROBOT_IP, DASHBOARD_PORT)
        move = DobotApiMove(ROBOT_IP, MOVE_PORT)
        print("Connection successful!")
        return dashboard, move
    except Exception as e:
        print("Connection failed :(")
        raise e

def enable_robot(dashboard):
    try:
        print("Enabling the robot...")
        if PARAMS == 0:
            dashboard.EnableRobot()
        else:
            # Load, CenterX, CenterY, CenterZ
            load = 0.1
            centerX = 0.1
            centerY = 0.1
            centerZ = 0.1
            dashboard.EnableRobot(load, centerX, centerY, centerZ)
        print("Robot enabled!")
    except Exception as e:
        print("Error during robot enabling :(")
        raise e

def disable_robot(dashboard):
    """
    # disable the robot.
    """
    dashboard.DisableRobot()
    print("Robot Disabled!")

def move_to_position(dashboard, move, position, speed_factor=100, tolerance=1.0):
    """
     Move to the given (x, y, z, r) position using MovL and return the time elapsed from the start to the end of that movement.
     1) Send the MovL command
     2) Wait until the robot reaches the destination (using GetPose())
     3) Return the elapsed time as a float
    """
    x, y, z, r = position
    print(f"\n[Action] --> {position}, SpeedFactor={speed_factor}")

    # Set SpeedFactor (overall percentage for all movements)
    #  - On the Dobot side, it’s a proportional setting from 1 to 100
    #  - Value can be 0.1–1.0 (or 1–100), depending on the documentation
    
    #dashboard.SpeedFactor(speed_factor)

    # other parameters for speed and acceleration
    dashboard.SpeedL(100)
    dashboard.AccL(1)

    # MovL 
    userparam   = "User=0"
    toolparam   = "Tool=0"
    speedlparam = "SpeedL=15"
    acclparam   = "AccL=1"
    cpparam     = "CP=100"

    start_time = time.time()

    
    move.MovL(x, y, z, r, userparam, toolparam, speedlparam, acclparam, cpparam)

    # wait for the robot to reach the target position
    while True:
        time.sleep(0.1)
        response = dashboard.GetPose()
        pose_vals = parse_pose(response)
        if pose_vals:
            curr_x, curr_y, curr_z, curr_r = pose_vals[:4]
            if (abs(curr_x - x) < tolerance and
                abs(curr_y - y) < tolerance and
                abs(curr_z - z) < tolerance and
                abs(curr_r - r) < tolerance):
                break

    end_time = time.time()
    duration = end_time - start_time
    print(f"Action completed, time: {duration:.2f} seconds")
    return duration

# ---------------------------------------------
# Excel preparation and saving
# ---------------------------------------------
def prepare_excel():
    """
    Creates a new Excel workbook and header row.
    """
    wb = Workbook()
    sheet = wb.active
    sheet.title = "Speed ​​Trials"

    # titles
    headers = [
        "Speed",             # Slow(10%), Medium(15%), Fast(25%)
        "Initial X",         # 300
        "Initial Y",         # 0
        "Initial Z",         # 100
        "Initial R",         # 0
        "End X",             # 300
        "End Y",             # 0
        "End Z",             # 0
        "End R",             # 0
        "Starting Time (s)", # 100->0 move
        "Stop Time (s)",     # 0.50 waiting time
        "End Time (s)"       # 0->100 return
    ]
    sheet.append(headers)
    return wb, sheet

def save_excel(wb, filename):
    wb.save(filename)
    print(f"Excel kaydedildi: {filename}")

# ---------------------------------------------
# main program
# ---------------------------------------------
if __name__ == "__main__":
   
    workbook, sheet = prepare_excel()

    
    dashboard, move = connect_robot()

    try:
        enable_robot(dashboard)

      
        for speed_name, speed_value in SPEED_LIST:
            print(f"\n===== Speed Test: {speed_name} ({speed_value}%) =====")

        
            starting_time = move_to_position(dashboard, move, P_DOWN, speed_factor=speed_value)

            stop_time = 0.20

            end_time = move_to_position(dashboard, move, P_UP, speed_factor=speed_value)

            row_data = [
                speed_name,
                P_UP[0],   # 300
                P_UP[1],   # 0
                P_UP[2],   # 100
                P_UP[3],   # 0
                P_DOWN[0], # 300
                P_DOWN[1], # 0
                P_DOWN[2], # 0
                P_DOWN[3], # 0
                round(starting_time, 2),
                round(stop_time, 2),
                round(end_time, 2)
            ]
            sheet.append(row_data)

    except KeyboardInterrupt:
        print("Kullanıcı iptal etti (CTRL+C).")
    except Exception as e:
        print(f"Hata oluştu: {e}")
    finally:
        disable_robot(dashboard)
        # save the Excel file
        save_excel(workbook, EXCEL_FILENAME)
