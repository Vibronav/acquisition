from flask import Flask, request, jsonify
from vnav_acquisition.interface import get_html
from vnav_acquisition.comm import on_rec_stop, on_rec_start, delete_last_recording
from vnav_acquisition.config import config
import random
import threading
import webbrowser
import argparse
import json
import os   # Berke 16.09.2024

app = Flask(__name__)


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
    #threading.Timer(1.25, lambda: webbrowser.open(url) ).start()
    
    # Berke 16.09.2024 writing the port number to a file
    port_file_path = os.path.join(os.path.dirname(__file__), 'flask_port.txt')
    with open(port_file_path, 'w') as f:
        f.write(str(port))
    # Berke 16.09.2024 writing the port number to a file
    
    app.run(port=port, debug=False)


if __name__ == '__main__':
    main()
