import cv2


def run():
    tracker = cv2.TrackerGOTURN_create()
    print(tracker)