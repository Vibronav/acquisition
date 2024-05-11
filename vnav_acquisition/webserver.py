from flask import Flask, request, jsonify
from robot import RunPoint, WaitArrive, ConnectRobot
from vnav_acquisition.interface import get_html
from vnav_acquisition.comm import on_rec_stop, on_rec_start, delete_last_recording
from vnav_acquisition.config import config
import random
import threading
import webbrowser
import argparse
import json

app = Flask(__name__)
dashboard, move, feed = ConnectRobot()

# Flag to indicate whether the robot is enabled or disabled
robot_enabled = True


@app.route("/", methods=['GET'])
def frontpage():
    return get_html(materials=config['materials'], speeds=config['speeds'])


@app.route("/stop", methods=['GET'])
def stop():
    recording_status = on_rec_stop()
    print("Received stop/GET request")
    return jsonify(recording_status)


@app.route("/start", methods=['POST'])
def start():
    params = json.loads(request.data.decode('utf-8'))  # Get the request data as a string
    print("Received start/POST request data:")
    print(params)
    file_name = on_rec_start(config['connection'], **params)
    return jsonify(file_name)


@app.route("/delete_last", methods=['GET'])
def delete_last():
    deleted_files = delete_last_recording()
    print("Received delete_last/GET request")
    return jsonify(deleted_files)


# Robot Controls

@app.route('/move', methods=['POST'])
def move_robot():
    global robot_enabled
    if robot_enabled:
        data = request.get_json()
        position = data['position']

        # Extracting only x and z coordinates, keeping y and r constant
        x, _, z, _ = position
        new_position = [x, 0, z, 78]  # Keeping y=0 and r=78

        RunPoint(move, new_position)

        # Wait for the robot to arrive at the specified position
        WaitArrive(new_position)

        return jsonify({'message': 'Robot arrived at position {}'.format(new_position)})
    else:
        return jsonify({'message': 'Robot is disabled. Cannot move.'}), 400


@app.route('/enable', methods=['POST'])
def enable_robot():
    global robot_enabled
    data = request.get_json()
    enable = data['enable']
    if enable:
        dashboard.EnableRobot()
        robot_enabled = True
        message = 'Robot enabled'
    else:
        dashboard.DisableRobot()
        robot_enabled = False
        message = 'Robot disabled'
    return jsonify({'message': message})


@app.route('/disable', methods=['POST'])
def disable_robot():
    global robot_enabled
    robot_enabled = False
    dashboard.DisableRobot()
    return jsonify({'message': 'Robot disabled'})


def main():
    parser = argparse.ArgumentParser(description="Web browser interface for synchronous acquisition of audio "
                                                 "(from rasberry_pi/banana_pi devboard) and video from webcam")
    parser.add_argument("--setup", help="Path to setup JSON file (if not provided or some fields are missing, default "
                                        "configuration is used.)",
                        default="")
    args = parser.parse_args()
    if args.setup:
        config.load_from_json(args.setup)

    port = 5000 + random.randint(0, 999)
    url = "http://127.0.0.1:{0}".format(port)
    threading.Timer(1.25, lambda: webbrowser.open(url)).start()
    app.run(port=port, debug=False)


if __name__ == '__main__':
    main()
