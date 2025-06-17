import cv2

tracker = None

def init_tracker(frame, bbox):
    global tracker
    tracker = cv2.TrackerGOTURN_create()
    tracker.init(frame, tuple(bbox))

def update_tracker(frame):
    global tracker
    if tracker is None:
        raise RuntimeError("Tracker not initialized. Call init_tracker first.")
    
    success, bbox = tracker.update(frame)
    return success, bbox