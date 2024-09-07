import cv2

def list_camera_indexes_and_names():
    index = 0
    found_camera = False

    print("Checking for connected cameras...")

    while True:
        # Try to open the camera at the given index
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            found_camera = True
            # Try to get camera name or other identifying information
            # Note: OpenCV doesn't provide camera names directly
            # We use backend info for this purpose if available
            backend = cap.get(cv2.CAP_PROP_BACKEND)
            print(f"Camera found at index {index}")

            # Attempt to print some information about the camera
            # This may not always be meaningful
            backend_name = "Unknown Backend"
            if backend == cv2.CAP_V4L:
                backend_name = "V4L (Video4Linux)"
            elif backend == cv2.CAP_DSHOW:
                backend_name = "DirectShow"
            elif backend == cv2.CAP_MSMF:
                backend_name = "Media Foundation"
            
            print(f"Backend used: {backend_name}")

            cap.release()
        else:
            # If opening the camera fails, we assume there are no more cameras
            if found_camera:
                print("No more cameras found.")
            break

        index += 1

if __name__ == "__main__":
    list_camera_indexes_and_names()
