import cv2
import numpy as np
import base64

tracker = None
pixels_per_cm = 20

def calibrate(frame, pattern_size=(7, 6), square_cm=2.0):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, pattern_size)
    if not ret:
        raise RuntimeError("Chessboard corners not found in the frame.")

    corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1),
                               (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1))
    
    dists = []
    for row in range(pattern_size[1]):
        for col in range(pattern_size[0] - 1):
            idx = row * pattern_size[0] + col
            p1 = corners[idx][0]
            p2 = corners[idx + 1][0]
            dists.append(np.linalg.norm(p2 - p1))

    mean_pix = float(np.mean(dists))
    return mean_pix / square_cm


def decode_frame(frame_data):

    _, b64 = frame_data.split(',', 1)
    png = base64.b64decode(b64)
    img_arr = np.frombuffer(png, dtype=np.uint8)
    frame = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
    return frame

def init_tracker(frame, bbox):
    global tracker, pixels_per_cm
    tracker = cv2.TrackerGOTURN_create()
    frame = decode_frame(frame)

    # pixels_per_cm = calibrate(frame, pattern_size=(7, 6), square_cm=2.0)
    
    x, y, w, h = bbox

    tracker.init(frame, (x, y, w, h))

def update_tracker(frame):
    global tracker, pixels_per_cm
    if tracker is None:
        raise RuntimeError("Tracker not initialized. Call init_tracker first.")
    
    frame = decode_frame(frame)
    success, bbox = tracker.update(frame)

    # x, y, w, h = bbox
    # x_cm = x / pixels_per_cm
    # y_cm = y / pixels_per_cm
    # w_cm = w / pixels_per_cm
    # h_cm = h / pixels_per_cm
    
    # bbox = (x_cm, y_cm, w_cm, h_cm)

    return success, bbox