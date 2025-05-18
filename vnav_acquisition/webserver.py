from flask import Flask, request, jsonify, send_from_directory
from vnav_acquisition.interface import get_html
from vnav_acquisition.comm import on_rec_stop, on_rec_start, delete_last_recording
from vnav_acquisition.config import config
from vnav_acquisition.automation_playwright import run_automation
import random
import threading
import webbrowser
import argparse
import json
import os   # Berke 16.09.2024
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR
PORT_FILE = BASE_DIR / "flask_port.txt"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")
app.config["JSON_AS_ASCII"] = False


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


@app.route("/stop", methods=['GET'])
def stop():
    print("Received stop/GET request")
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


@app.route("/run", methods=["POST"])
def run():
    print("Received run/POST request")
    params = request.get_json(force=True)
    print(f'With params: {params}')

    required = ("username", "material", "speed", "iterations")
    if not all(param in params for param in required):
        return jsonify({"error": "Missing parameters"}), 400
    
    t = threading.Thread(
        target=run_automation,
        kwargs=dict(
            username = params["username"],
            material = params["material"],
            speed = params["speed"],
            position_type = "Only Up and Down",
            p1 = (300, 0, -20, 0),
            p2 = (0, 0, 0, 0),
            p3 = (300, 0, -90, 0),
            num_iterations = params["iterations"]
        ),
        daemon=True
    )

    t.start()

    return jsonify({"status": "started"})




@app.route("/delete_last", methods=['GET'])
def delete_last():
    deleted_files = delete_last_recording()
    print("Received delete_last/GET request")
    return jsonify(deleted_files)


def parse_args():
    parser = argparse.ArgumentParser(description="Web browser interface for synchronous acquisition of audio "
                                                 "(from rasberry_pi/banana_pi devboard) and video from webcam")
    parser.add_argument("--setup", help="Path to setup JSON file (if not provided or some fields are missing, default "
                                        "configuration is used.)", default="")
    parser.add_argument("--port", type=int, help="Port (default 5000)", default=5000)
    parser.add_argument("--open-browser", action="store_true", help="Open browser after start")
    return parser.parse_args()

def main():
    args = parse_args()

    if args.setup:
        config.load_from_json(args.setup)

    # port = 5000 + random.randint(0, 999)
    port = args.port
    url = "http://127.0.0.1:{0}".format(port)

    PORT_FILE.write_text(str(port), encoding="utf-8")

    if args.open_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url), ).start()
    
    app.run(port=port, debug=False)


if __name__ == '__main__':
    main()