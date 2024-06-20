import threading
from flask import Flask, request, jsonify, send_from_directory, url_for, send_from_directory, render_template_string
from flask_cors import CORS
from comm import on_rec_stop, on_rec_start, delete_last_recording
from config import config
import argparse
import os
import webbrowser


app = Flask(__name__, static_folder='../front_app/dist')
# Configure CORS using Flask-CORS (adjust origins as needed)
# Replace with your React app origin
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
    # TODO config._config is not working for some reason
    return jsonify(config._DEFAULT_CONFIG)


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

# will serve recorded files
@app.route('/api/audio/<filename>', methods=['GET'])
def get_audio_file(filename):
    return send_from_directory(config["local_dir"], filename)


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
    file_name =  on_rec_start(config['connection'], *params)
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

    url = "http://127.0.0.1:5000"
    threading.Timer(1.25, lambda: webbrowser.open(url)).start()
    app.run(port=5000, debug=False)


if __name__ == '__main__':
    main()
