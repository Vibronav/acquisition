import cv2
import numpy as np
import base64

tracker = None

def decode_frame(frame_data):

    _, b64 = frame_data.split(',', 1)
    png = base64.b64decode(b64)
    img_arr = np.frombuffer(png, dtype=np.uint8)
    frame = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
    return frame

def init_tracker(frame, bbox):
    global tracker
    tracker = cv2.TrackerGOTURN_create()
    frame = decode_frame(frame)
    tracker.init(frame, tuple(bbox))

def update_tracker(frame):
    global tracker
    if tracker is None:
        raise RuntimeError("Tracker not initialized. Call init_tracker first.")
    
    frame = decode_frame(frame)
    success, bbox = tracker.update(frame)
    return success, bbox