from flask import Flask, request, jsonify
from vnav_acquisition.interface import get_html
from vnav_acquisition.comm import on_rec_stop, on_rec_start
from vnav_acquisition.config import config
import random
import threading
import webbrowser
import os
import argparse
import json

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", help="Setup JSON file",
                        default=os.path.join(os.path.dirname(__file__), "setup.json"))
    args = parser.parse_args()
    config.load_from_json(args.setup)

    port = 5000 + random.randint(0, 999)
    url = "http://127.0.0.1:{0}".format(port)
    threading.Timer(1.25, lambda: webbrowser.open(url) ).start()
    app.run(port=port, debug=False)


if __name__ == '__main__':
    main()
