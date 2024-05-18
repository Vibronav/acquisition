from flask import Flask, request, jsonify
from flask_cors import CORS
from vnav_acquisition.interface import get_html
from vnav_acquisition.comm import on_rec_stop, on_rec_start, delete_last_recording
from vnav_acquisition.config import config
import threading
import webbrowser
import argparse
import json

app = Flask(__name__)
# Configure CORS using Flask-CORS (adjust origins as needed)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173"]}})  # Replace with your React app origin

@app.route("/api/parse_config", methods=['GET'])
def parse_config():
    print("Received parse_config/GET request")
    return jsonify(config._DEFAULT_CONFIG) #TODO config._config is not working for some reason

@app.route("/api/stop", methods=['GET'])
def stop():
    recording_status = on_rec_stop()
    print("Received stop/GET request")
    return jsonify(recording_status)


@app.route("/api/start", methods=['POST'])
def start():
     # Parse the incoming JSON data
    data = request.get_json()

    # Extract the parameters as an array of strings
    params = [
        data.get('username', ''),
        data.get('material', ''),
        data.get('speed', '')
    ]
    print("Received start/POST request data:")
    print( params)
    file_name = on_rec_start(config['connection'], *params)
    return jsonify(file_name)


@app.route("/api/delete_last", methods=['GET'])
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

    app.run(port=5000, debug=True)


if __name__ == '__main__':
    main()
