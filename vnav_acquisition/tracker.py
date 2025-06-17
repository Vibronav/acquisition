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

    x, y, w, h = bbox
    vis = frame.copy()
    print(frame.shape)
    print(f"Initializing tracker with bbox: {bbox}")
    cv2.rectangle(vis, (int(x), int(y)), (int(x + w), int(y + h)), (255, 0, 0), 2)
    cv2.imshow("Tracker Init", vis)
    cv2.waitKey(1)

    tracker.init(frame, tuple(bbox))

def update_tracker(frame):
    global tracker
    if tracker is None:
        raise RuntimeError("Tracker not initialized. Call init_tracker first.")
    
    frame = decode_frame(frame)
    success, bbox = tracker.update(frame)
    return success, bbox