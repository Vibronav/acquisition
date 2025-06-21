from .comm import on_rec_start, on_rec_stop
from .config import config
import time

def start_recording(output_filename_prefix, socketio_instance):

    video_filename = f"{output_filename_prefix}.mp4"
    audio_filename = f"{output_filename_prefix}.wav"

    socketio_instance.emit("record", {
        "action": "start",
        "filename": video_filename
    })

    # is_started = on_rec_start(config['connection'], socketio_instance, audio_filename)
    is_started = True
    if not is_started:
        socketio_instance.emit("record", {
            "action": "stop",
            "shouldUpload": False
        })
        return False
    
    return True

def stop_recording(socketio_instance):
    # is_recorded = on_rec_stop()
    is_recorded = True
    if not is_recorded:
        socketio_instance.emit("record", {
            "action": "stop",
            "shouldUpload": False
        })
    else:
        time.sleep(0.5)
        socketio_instance.emit("record", {
            "action": "stop",
            "shouldUpload": True
        })