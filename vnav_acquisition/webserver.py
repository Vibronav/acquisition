import base64
import random
import threading
from flask import Flask, request, jsonify, send_from_directory, url_for, send_from_directory, render_template_string
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from .comm import on_rec_stop, on_rec_start, delete_last_recording
from .config import app_config
import argparse
import os
import webbrowser
from .audio_stream import start_recording, data_listener, parse_data
import numpy as np
from .automation import run_automation
import time


app = Flask(__name__, static_folder='front_app/dist')
socketio = SocketIO(app, cors_allowed_origins="*")  # Initialize SocketIO instance

# Configure CORS using Flask-CORS (adjust origins as needed)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173","http://127.0.0.1:5000"]}})



@app.after_request
def add_security_headers(response):
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    return response

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route("/api/parse_config", methods=['GET'])
def parse_config():
    print("Received parse_config/GET request")
    return jsonify(app_config._config)


# WebSocket route for NumPy streaming
@app.route("/api/audio_stream", methods=['GET'])
def handle_connect():
    #data_to_send = parse_data()  # Convert NumPy array to list for JSON serialization

    # return jsonify({
    #     "audio_channel1": data_to_send[0].tolist(),
    #     "audio_channel2": data_to_send[1].tolist()
    # })

    #===== Stub audio ==========
    # Parameters

    frequency = random.randint(240, 450)  # Frequency of the sine wave (in Hz)
    sample_rate = 44100  # Sample rate (in samples per second)
    duration = 1024 / sample_rate  # Duration in seconds for 1024 samples

    # Generate time values for 1024 samples
    t = np.linspace(0, duration, 1024, endpoint=False)

    # Generate the sine wave
    sine_wave = np.sin(2 * np.pi * frequency * t)

    return jsonify({
        "audio_channel1": sine_wave.tolist(),
        "audio_channel2": sine_wave.tolist()
     })
        


# will serve recorded files
@app.route('/api/audio/<filename>', methods=['GET'])
def get_audio_file(filename):
    return send_from_directory(app_config["local_dir"], filename)

@app.route("/api/start_dobot", methods=['POST'])
def start_dobot():
    # Parse the incoming JSON data
    data = request.get_json()

    # Extract the parameters as an array of strings
    params_record = [
        data.get('username', ''),
        data.get('material', ''),
        data.get('speed', '')
    ]

    params_dobot = [
        data.get('speed', ''),
        data.get('positionType', ''),
        data.get('P1', ''),
        data.get('P2', ''),
        data.get('P3', '')
    ]
    
    print("Received start_dobot/POST request data:")
    print("params_record ", params_record)
    print("params_dobot ",params_dobot)
 
    thread_record = threading.Thread(target=on_rec_start, args=(app_config['connection'], *params_record))
    thread_record.start()
    time.sleep(2) #for debug only
    #run_automation(*params_dobot)
    thread_record.join()

    return jsonify('Recording started')


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
    print(params)
    file_name = on_rec_start(app_config['connection'], *params)

    return jsonify(file_name)



@app.route("/api/stop", methods=['GET'])
def stop():
    recorded_files = on_rec_stop()
    print("Received stop/GET request")
    print(recorded_files)
    
    # Create URLs for each recorded file
    recorded_files_with_urls = [
        {"filename": filename, "url": url_for('get_audio_file', filename=filename, _external=True)}
        for filename in recorded_files
    ]
    
    return jsonify(recorded_files_with_urls)

@app.route("/api/delete_last", methods=['GET'])
def delete_last():
    deleted_files = delete_last_recording()
    print("Received delete_last/GET request")
    return jsonify(deleted_files)

@app.route("/api/save_video", methods=['POST'])
def save_video():
    # Parse the incoming JSON data
    data = request.get_json()

    filename = data.get('filename', '')
    local_dir = data.get('local_dir', '')
    base64_data = data.get('data', '')

    # Check if the directory exists, create it if it doesn't
    try:
        os.makedirs(os.path.abspath(local_dir), exist_ok=True)  # This will create the directory if it doesn't exist
    except Exception as e:
        print(f"Error creating directory: {e}")
        local_dir = os.getcwd()  # Fall back to the current working directory

    # Decode base64 data and save it as a file
    if base64_data:
        video_data = base64.b64decode(base64_data)
        with open(os.path.join(local_dir,filename), 'wb') as f:
            f.write(video_data)

    print(f"Received save_video/POST request for filename: {local_dir}/{filename}")
    return jsonify({"filename": os.path.join(local_dir,filename), "status": "saved"})


def main():
  
    parser = argparse.ArgumentParser(description="Web browser interface for synchronous acquisition of audio "
                                                 "(from rasberry_pi/banana_pi devboard) and video from webcam")
    parser.add_argument("--setup", help="Path to setup JSON file (if not provided or some fields are missing, default "
                                        "configuration is used.)",
                        default="")
    args = parser.parse_args()
    if args.setup:
        app_config.load_from_json(args.setup)

    # audio_out = start_recording()
    # threading.Thread(target=data_listener, args=(audio_out,), daemon=True).start()

    url = "http://127.0.0.1:5000"
    # recorder.run()
    threading.Timer(1.25, lambda: webbrowser.open(url)).start()
    socketio.run(app, port=5000, debug=False)


if __name__ == '__main__':
    main()
