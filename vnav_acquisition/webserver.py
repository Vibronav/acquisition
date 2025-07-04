import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, send_from_directory
from vnav_acquisition.comm import is_ssh_connected, ssh_connect, on_rec_start, on_rec_stop
from vnav_acquisition.config import config
from vnav_acquisition.runtime_config import runtime_config
from vnav_acquisition.automation import safe_run_automation
from .record import start_recording, stop_recording, delete_last_recording
from .utils import build_filename
import threading
import webbrowser
import argparse
import os   # Berke 16.09.2024
from pathlib import Path
from flask_socketio import SocketIO
import sounddevice as sd
import time


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")
app.config["JSON_AS_ASCII"] = False

socketio = SocketIO(app, cors_allowed_origins="*")

automation_thread = None
stop_event = threading.Event()


@app.route("/upload", methods=['POST'])
def upload_video():
    print(f'Received upload request')
    file = request.files['file']
    filename = file.filename
    video_output_dir = os.path.join(os.getcwd(), "videos")
    os.makedirs(video_output_dir, exist_ok=True)

    file_path = os.path.join(video_output_dir, filename)
    file.save(file_path)
    print(f"File saved to {file_path}")
    return jsonify({"status": "ok", "filename": filename})


@app.route("/", methods=['GET'])
def frontpage():
    return send_from_directory(STATIC_DIR, "index.html")

@app.route("/config", methods=['GET'])
def api_config():
    print("Received config/GET request")
    return jsonify({
        "materials": config["materials"],
        "speeds": config["speeds"],
        "needleTypes": config["needleTypes"],
        "microphoneTypes": config["microphoneTypes"]
    })

@app.route("/run", methods=["POST"])
def run():
    global automation_thread, stop_event
    print("Received run/POST request")
    params = request.get_json(force=True)
    print(f'With params: {params}')

    required = ("material", "speed", "needleType", "iterations", "initX", "finishX", "upZ", "downZ", "motionType")
    if not all(param in params for param in required):
        return jsonify({"error": "Missing parameters"}), 400
    
    stop_event.clear()
    automation_thread = threading.Thread(
        target=safe_run_automation,
        kwargs=dict(
            material = params["material"],
            needle_type = params["needleType"],
            microphone_type = params["microphoneType"],
            description = params["description"],
            stop_event = stop_event,
            initX = params.get("initX"),
            finishX = params.get("finishX"),
            upZ = params.get("upZ"),
            downZ = params.get("downZ"),
            speed = int(params["speed"]),
            motion_type = params["motionType"],
            num_iterations = params["iterations"],
            socketio_instance=socketio
        ),
        daemon=True
    )

    automation_thread.start()

    return jsonify({"status": "started"})


@app.route("/stop", methods=['POST'])
def stop():
    print("Received stop/POST request")
    stop_event.set()
    return jsonify({"status": "Will stop after current iteration."})


@app.route("/raspberry-status", methods=['GET'])
def check_connection():
    import logging
    werkzeug_log = logging.getLogger('werkzeug')
    prev_level = werkzeug_log.level
    werkzeug_log.setLevel(logging.ERROR)

    try:
        is_connected = is_ssh_connected()
        if is_connected:
            return jsonify({"status": "connected"})
        else:
            return jsonify({"status": "not connected"})
    finally:
        werkzeug_log.setLevel(prev_level)

@app.route("/set-micro-output", methods=['POST'])
def set_micro_output():
    print("Received set-micro-output/POST request")
    params = request.get_json(force=True)
    print(f'With params: {params}')
    output_name = params.get("micro_output")

    if not output_name:
        return jsonify({"error": "Missing 'micro_output' parameter"}), 400
    
    for idx, dev in enumerate(sd.query_devices()):
        if output_name in dev['name'] and dev['max_output_channels'] > 0:
            runtime_config.set_value('micro_output', idx)
            return jsonify({"status": "ok", "micro_output": idx})
        
    return jsonify({"error": f"Audio output '{output_name}' not found"}), 404

@app.route('/get-audio-outputs', methods=['GET'])
def get_audio_outputs():
    print("Received get-audio-outputs/GET request")
    seen = set()
    outputs = []
    default_hostapi = sd.default.hostapi

    for idx, dev in enumerate(sd.query_devices()):
        name = dev['name'].strip()
        if (dev['max_output_channels'] > 0 
            and name 
            and name not in seen
            and dev['hostapi'] == default_hostapi):
            outputs.append({'name': name})
            seen.add(name)

    print(f"Available audio outputs: {outputs}")
    return jsonify(outputs)

@app.route('/start-recording', methods=['POST'])
def post_start_recording():
    print("Received start-recording/POST request")

    params = request.get_json(force=True)
    print(f'With params: {params}')

    username = params.get("username")
    material = params.get("material")
    needle_type = params.get("needleType")
    microphone_type = params.get("microphoneType")
    description = params.get("description")
    output_filename_prefix = build_filename(username, description, material, needle_type, microphone_type)

    is_started = start_recording(output_filename_prefix, socketio)
    if not is_started:
        return jsonify({"error": "Recording could not be started"}), 400
    
    return jsonify({"status": "ok"})


@app.route('/stop-recording', methods=['POST'])
def post_stop_recording():
    print("Received stop-recording/POST request")
    
    stop_recording(socketio)
    return jsonify({"status": "ok"})

@app.route('/delete-last-recording', methods=['POST'])
def post_delete_last_recording():
    print("Received delete-last-recording/POST request")
    
    message = delete_last_recording()
    if message == "":
        return jsonify({"status": "not found", "message": "No recordings to delete."})
    return jsonify({"status": "ok", "message": message})


def parse_args():
    parser = argparse.ArgumentParser(description="Web browser interface for synchronous acquisition of audio "
                                                 "(from rasberry_pi/banana_pi devboard) and video from webcam")
    parser.add_argument("--setup", help="Path to setup JSON file (if not provided or some fields are missing, default "
                                        "configuration is used.)", default="")
    parser.add_argument("--port", type=int, help="Port (default 5000)", default=5000)
    return parser.parse_args()

def main():
    args = parse_args()

    if args.setup:
        config.load_from_json(args.setup)

    port = args.port
    url = "http://127.0.0.1:{0}".format(port)

    ssh_connect(*config['connection'], socketio_instance=socketio)

    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    
    socketio.run(app, port=port, debug=False)


if __name__ == '__main__':
    main()