from .comm import on_rec_start, on_rec_stop
from .config import config
import time

def start_recording(output_filename, socketio_instance, username=None, material=None, speed=None):
    socketio_instance.emit("record", {
        "action": "start",
        "filename": output_filename
    })

    is_started = on_rec_start(config['connection'], socketio_instance, username, material, speed)
    if not is_started:
        socketio_instance.emit("record", {
            "action": "stop",
            "shouldUpload": False
        })
        return False
    
    return True

def stop_recording(socketio_instance):
    is_recorded = on_rec_stop()
    if not is_recorded:
        socketio_instance.emit("record", {
            "action": "stop",
            "shouldUpload": False
        })
    else:
        time.sleep(2.5)
        socketio_instance.emit("record", {
            "action": "stop",
            "shouldUpload": True
        })