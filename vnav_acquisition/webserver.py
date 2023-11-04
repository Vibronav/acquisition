from flask import Flask, request
from vnav_acquisition.interface import get_html
from vnav_acquisition.comm import on_rec_stop, on_rec_start
import json
import random, threading, webbrowser


app = Flask(__name__)


@app.route("/", methods=['GET'])
def test():
    return get_html()


@app.route("/stop", methods=['GET'])
def stop():
    on_rec_stop()
    print("Received stop/GET request")
    return "OK stop"


@app.route("/start", methods=['POST'])
def start():
    params = json.loads(request.data.decode('utf-8'))  # Get the request data as a string
    print("Received start/POST request data:")
    print(params)
    on_rec_start(**params)
    return "OK start"


def main():
    port = 5000 + random.randint(0, 999)
    url = "http://127.0.0.1:{0}".format(port)
    threading.Timer(1.25, lambda: webbrowser.open(url) ).start()
    app.run(port=port, debug=False)


if __name__ == '__main__':
    main()
