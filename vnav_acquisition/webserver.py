import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, send_from_directory
from vnav_acquisition.comm import is_ssh_connected, ssh_connect
from vnav_acquisition.config import config
from vnav_acquisition.automation import safe_run_automation
import threading
import webbrowser
import argparse
import os   # Berke 16.09.2024
from pathlib import Path
from flask_socketio import SocketIO


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR
PORT_FILE = BASE_DIR / "flask_port.txt"

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
        "speeds": config["speeds"]
    })

@app.route("/run", methods=["POST"])
def run():
    global automation_thread, stop_event
    print("Received run/POST request")
    params = request.get_json(force=True)
    print(f'With params: {params}')

    required = ("username", "material", "speed", "iterations")
    if not all(param in params for param in required):
        return jsonify({"error": "Missing parameters"}), 400
    
    stop_event.clear()
    automation_thread = threading.Thread(
        target=safe_run_automation,
        kwargs=dict(
            username = params["username"],
            material = params["material"],
            stop_event = stop_event,
            speed = params["speed"],
            motion_type = params["motionType"],
            p1 = tuple(params["p1"]),
            p2 = tuple(params["p2"]),
            p3 = tuple(params["p3"]),
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

    PORT_FILE.write_text(str(port), encoding="utf-8")

    ssh_connect(*config['connection'], socketio_instance=socketio)

    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    
    socketio.run(app, port=port, debug=False)


if __name__ == '__main__':
    main()