import cv2
import numpy as np
import base64
from sklearn.linear_model import LinearRegression

### Code for later testing
"""

tracker = None
pixel_distances1, cm_distances1 = [], []
calibration_model = LinearRegression()

def calibrate(frame, pattern_size=(7, 6), square_cm=2.0):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, pattern_size)
    if not ret:
        raise RuntimeError("Chessboard corners not found in the frame.")

    corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1),
                               (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1))
    
    pixel_distances = []
    cm_distances = []
    for row in range(pattern_size[1]):
        for col in range(pattern_size[0] - 1):
            idx = row * pattern_size[0] + col
            p1 = corners[idx][0]
            p2 = corners[idx + 1][0]
            pixel_distances.append(np.linalg.norm(p2 - p1))
            cm_distances.append((col + 1) * square_cm)

    return pixel_distances, cm_distances


def decode_frame(frame_data):

    _, b64 = frame_data.split(',', 1)
    png = base64.b64decode(b64)
    img_arr = np.frombuffer(png, dtype=np.uint8)
    frame = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
    return frame

def init_tracker(frame, bbox):
    global tracker, pixel_distances1, cm_distances1, calibration_model
    tracker = cv2.TrackerGOTURN_create()
    frame = decode_frame(frame)

    pixel_distances1, cm_distances1 = calibrate(frame, pattern_size=(7, 6), square_cm=2.0)
    calibration_model.fit(pixel_distances1, cm_distances1)

    x, y, w, h = bbox
    cy = y + h // 2
    cy_cm = calibration_model.predict([[cy]])[0]

    tracker.init(frame, (x, y, w, h))
    return cy_cm

def update_tracker(frame):
    global tracker, calibration_model
    if tracker is None:
        raise RuntimeError("Tracker not initialized. Call init_tracker first.")
    
    frame = decode_frame(frame)
    success, bbox = tracker.update(frame)

    _, y, _, h = bbox
    cy = y + h // 2
    cy_cm = calibration_model.predict([[cy]])[0]

    return success, bbox, cy_cm

"""

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

    pixels_per_cm = calibrate(frame, pattern_size=(7, 6), square_cm=2.0)
    
    x, y, w, h = bbox
    cy = y + (h // 2)
    cy_cm = cy / pixels_per_cm
    print(f'Initializing tracker with cy: {cy}')

    tracker.init(frame, (x, y, w, h)), cy_cm

def update_tracker(frame):
    global tracker, pixels_per_cm
    if tracker is None:
        raise RuntimeError("Tracker not initialized. Call init_tracker first.")
    
    frame = decode_frame(frame)
    success, bbox = tracker.update(frame)

    _, y, _, h = bbox
    cy = y + (h // 2)
    print(f'Updating tracker with cy: {cy}')
    cy_cm = cy / pixels_per_cm
    
    return success, bbox, cy_cm