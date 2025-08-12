import argparse
import os
import cv2
import cv2.aruco as aruco
import pandas as pd
import numpy as np
from tqdm.auto import tqdm
import json

camera_matrix = np.array([[630.41, 0.0, 640],
                            [0.0, 631.93, 353],
                            [0.0, 0.0, 1.0]])

dist_coeffs = np.array([0.14, -0.44, 0.0, 0.0, 0.31])

def show_video_frame(frame, fps, display):
    if not display:
        return True

    cv2.imshow('Aruco Tracking', frame)
    sleep_time = 1000 // fps
    key = cv2.waitKey(sleep_time) & 0xFF
    return key != ord("q")

def process_data(df, video_path, positions_folder, annotations_folder, distances_file_path, fps=30):
    os.makedirs(positions_folder, exist_ok=True)
    os.makedirs(annotations_folder, exist_ok=True)

    video_name = os.path.splitext(os.path.basename(video_path))[0]

    calculate_speed(df, fps=fps)
    positions_output_path = os.path.join(positions_folder, f'{video_name}.csv')

    df.to_csv(positions_output_path, index=False)

    create_annotations(df, video_name, annotations_folder, distances_file_path)

def calculate_speed(df, fps=30, frame_interval=1):
    dt = frame_interval / fps

    df['dx'] = df['Object_X_cm'].shift(-frame_interval) - df['Object_X_cm']
    df['dy'] = df['Object_Y_cm'].shift(-frame_interval) - df['Object_Y_cm']
    df['dz'] = df['Object_Z_cm'].shift(-frame_interval) - df['Object_Z_cm']

    df['velocity'] = df['dy'] / dt
    df['velocity_all'] = np.sqrt(df['dx']**2 + df['dy']**2 + df['dz']**2) / dt

    return df

def create_annotations(df, video_name, annotations_folder, distances_file_path):
    df.reset_index(drop=True, inplace=True)
    distances = read_distances_from_file(distances_file_path)
    if distances:
        annotations = {}

        min_high = df["Object_Y_cm"].dropna().idxmin()
        df_down = df.loc[:min_high]

        tracked_high = df_down[df_down['Object_Y_cm'].notna()]

        for idx, distance in enumerate(distances, start=1):
            diffs = (tracked_high['Object_Y_cm'] - distance).abs()
            best_row = df_down.loc[diffs.idxmin()]
            annotations[str(idx)] = {
                "frame": best_row["Frame"],
                "time": best_row["Time (s)"]
            }
        
    annotations_output_path = os.path.join(annotations_folder, f'{video_name}.json')
    payload = {
        "video_file": f'{video_name}.mp4',
        "video_annotations": annotations
    }
    with open(annotations_output_path, "w") as f:
        json.dump(payload, f, indent=4)

def read_distances_from_file(file_path):
    try:
        with open(file_path, 'r') as f:
            raw = f.read().strip()
        distances = [float(distance.strip()) for distance in raw.split(',') if distance.strip() != ""]
        return distances
    except Exception as e:
        print(f"Error reading distances from file {file_path}: {e}")
        return []

"""
Tracking without cube section
"""

def track_aruco_no_cube(video_path, dobot_mode, needle_length, marker_length_obj=4, axis_length=4, starting_position=14, fps=30, display=True):

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return pd.DataFrame()

    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    params = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(dictionary, params)

    height_constraint = None
    results = []
    frame_idx = 1
    marker_margin = 2.95
    claw = 1.2
    attachment = 0.69
    dobot_offset = marker_margin + claw + attachment

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        corners, ids, _ = detector.detectMarkers(frame)
        corners = list(corners)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        for i, c in enumerate(corners):
            corners[i] = cv2.cornerSubPix(
                gray, c,
                winSize=(5,5),
                zeroZone=(-1,-1),
                criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 300, 0.001)
            )        
        if ids is not None and len(ids) > 0:
            aruco.drawDetectedMarkers(frame, corners, ids)
            rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(corners, marker_length_obj, camera_matrix, dist_coeffs)

            if dobot_mode:
                r_o = rvecs[0].reshape(3, 1)
                t_o = tvecs[0].reshape(3, 1)
                R_o, _ = cv2.Rodrigues(r_o)
                t_o = (R_o @ np.array([[0.0, 0.0, -2.2]], dtype=np.float32).T + t_o).flatten()
                t_final = (np.array([0.0, dobot_offset + needle_length, 0.0], dtype=np.float32) + t_o)

                x = t_final[0]
                y = (t_final[1] * -1)
                z = t_final[2]
            else:
                needle_coord = np.array([[0.0, -needle_length, -0.9]], dtype=np.float32)
                
                r_o = rvecs[0].reshape(3, 1)
                t_o = tvecs[0].reshape(3, 1)
                R_o, _ = cv2.Rodrigues(r_o)

                t_final = (R_o @ needle_coord.T + t_o).flatten()

                x = t_final[0]
                y = (t_final[1] * -1)
                z = t_final[2]

            if height_constraint is None:
                height_constraint = y

            y = y - height_constraint + starting_position

            ### Helper line to labelling
            pts = corners[0].reshape(-1, 2)
            cx, cy = pts.mean(axis=0).astype(int)
            h, w = frame.shape[:2]
            cv2.line(frame, (0, cy), (w, cy), (0, 255, 0), 1)

            tip2d, _ = cv2.projectPoints(
                np.array([t_final], dtype=np.float32),
                np.zeros((3, 1)), np.zeros((3, 1)),
                camera_matrix, dist_coeffs
            )
            u, v = tip2d.ravel().astype(int)

            cv2.line(frame, (0, v), (w, v), (0, 255, 0), 1)            
            ### Helper line to labelling

            cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, r_o, t_o, axis_length)

            text = f'Position: X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}'
            corner = tuple(corners[0][0][0].astype(int))
            cv2.putText(frame, text, (corner[0], corner[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            results.append([frame_idx, round(frame_idx / fps, ndigits=2), x, y, z])
        else:
            results.append([frame_idx, round(frame_idx / fps, ndigits=2), None, None, None])

        cv2.imwrite(f'tracked_frames/frame_{frame_idx}.jpg', frame)

        if not show_video_frame(frame, fps, display):
            break

        frame_idx += 1

    cap.release()
    cv2.destroyAllWindows()
    df = pd.DataFrame(results, columns=['Frame', 'Time (s)', 'Object_X_cm', 'Object_Y_cm', 'Object_Z_cm'])
    return df

"""
Tracking with cube section
"""

def make_corners(xc, yc, zc, m_len, axis):
    """
    Order: [left-top, right-top, right-bottom, left-bottom]
    """
    mh = m_len / 2.00

    if axis == 'x-': # LEFT
        return np.array([
            [xc, yc + mh, zc - mh + 0.1],  # left-top
            [xc, yc + mh, zc + mh + 0.1],  # right-top
            [xc, yc - mh, zc + mh + 0.1],  # right-bottom
            [xc, yc - mh, zc - mh + 0.1]   # left-bottom
        ])
    elif axis == 'x+': # RIGHT
        return np.array([
            [xc, yc + mh, zc + mh],  # left-top
            [xc, yc + mh, zc - mh],  # right-top
            [xc, yc - mh, zc - mh],  # right-bottom
            [xc, yc - mh, zc + mh]   # left-bottom
        ])
    elif axis == 'y': # UP / DOWN
        return np.array([
            [xc - mh, yc, zc - mh],  # left-top
            [xc + mh, yc, zc - mh],  # right-top
            [xc + mh, yc, zc + mh],  # right-bottom
            [xc - mh, yc, zc + mh]   # left-bottom
        ])
    elif axis == 'z': # FRONT / BACK
        return np.array([
            [xc - mh, yc + mh, zc],  # left-top
            [xc + mh, yc + mh, zc],  # right-top
            [xc + mh, yc - mh, zc],  # right-bottom
            [xc - mh, yc - mh, zc]   # left-bottom
        ])

def detect_cube_pose(frame, detector, obj_pts_dict, camera_matrix, dist_coeffs, min_markers=2):

    corners, ids, _ = detector.detectMarkers(frame)
    if ids is None:
        return None
    
    all_obj, all_img = [], []
    for c, mid in zip(corners, ids.flatten()):
        if mid in obj_pts_dict:
            all_obj.append(obj_pts_dict[mid])
            all_img.append(c.reshape(-1, 2))
    if len(all_obj) < min_markers:
        return None
    
    obj_pts = np.vstack(all_obj)
    img_pts = np.vstack(all_img)
    _, rvec, tvec = cv2.solvePnP(obj_pts, img_pts, camera_matrix, dist_coeffs)

    R_c, _ = cv2.Rodrigues(rvec)

    return rvec, tvec, R_c.T, corners, ids

def track_aruco_cube(
        video_path,
        dobot_mode,
        needle_length, 
        marker_length_obj=4, 
        axis_length=4, 
        marker_length_cube=3, 
        cube_edge_top=5.0,
        cube_edge_sides=5,
        fps=30, 
        display=True):
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return pd.DataFrame()
    
    params = aruco.DetectorParameters()

    dict_cube = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)
    detector_cube = aruco.ArucoDetector(dict_cube, params)
    dict_marker = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    detector_obj = aruco.ArucoDetector(dict_marker, params)

    half_edge = cube_edge_top / 2.0
    half_edge_sides = cube_edge_sides / 2.0
    obj_pts_dict = {
        0: make_corners(0.0, half_edge, 0.0, marker_length_cube, 'y'), # TOP
        1: make_corners(0.0, 0.0, half_edge_sides, marker_length_cube, 'z'), # FRONT
        2: make_corners(-half_edge_sides, 0.0, 0.0, marker_length_cube, 'x-') # LEFT
    }

    cube_data = None
    init_frame = None

    cube_detection_attempts = 0
    while cube_data is None:
        ret, frame = cap.read()
        if not ret:
            print(f'Could not find cube in video: {video_path}')
            return pd.DataFrame()
        
        cube_data = detect_cube_pose(frame, detector_cube, obj_pts_dict, camera_matrix, dist_coeffs)
        init_frame = frame.copy()
        cube_detection_attempts += 1

    rvec_c, tvec_c, R_inv, corners_c, ids_c = cube_data
    r_c = rvec_c.flatten()
    t_c = tvec_c.flatten()
    x_c, y_c, z_c = t_c
    text = f'Cube Position: X: {x_c:.2f}cm, Y: {y_c:.2f}cm, Z: {z_c:.2f}cm'
    cv2.putText(init_frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    origin3d = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)

    corners3d = []
    colors = []

    for fid, pts3d in obj_pts_dict.items():
        corners3d.append(pts3d)

        if fid == 0:  # TOP
            col = (0, 255, 0)  # green
        elif fid == 1:  # FRONT
            col = (255, 0, 0)  # blue
        elif fid == 2:  # LEFT
            col = (0, 0, 255)  # red
        elif fid == 3:  # RIGHT
            col = (0, 255, 255)  # yellow
        colors += [col] * 4

    corners3d = np.vstack(corners3d).astype(np.float32)

    all3d = np.vstack([origin3d, corners3d])
    all2d, _ = cv2.projectPoints(
        all3d, rvec_c, tvec_c, camera_matrix, dist_coeffs
    )

    all2d = all2d.reshape(-1, 2).astype(int)

    cx, cy = all2d[0]
    cv2.circle(init_frame, (cx, cy), 6, (255, 255, 255), -1)

    for pt, col in zip(all2d[1:], colors):
        cv2.circle(init_frame, tuple(pt), 2, col, -1)


    aruco.drawDetectedMarkers(init_frame, corners_c, ids_c)
    cv2.drawFrameAxes(init_frame, camera_matrix, dist_coeffs, rvec_c, tvec_c, axis_length)
    if display:
        cv2.imshow('Cube Detection', init_frame)
        cv2.waitKey(5000)

    results = []
    frame_idx = 1
    marker_margin = 2.95
    claw = 1.2
    attachement = 0.69
    dobot_offset = marker_margin + claw + attachement

    cap.release()
    cap = cv2.VideoCapture(video_path)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        corners_o, ids_o, _ = detector_obj.detectMarkers(frame)
        corners_o = list(corners_o)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        for i, c in enumerate(corners_o):
            corners_o[i] = cv2.cornerSubPix(
                gray, c,
                winSize=(5,5),
                zeroZone=(-1,-1),
                criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            )
        if ids_o is not None and len(ids_o) > 0:
            aruco.drawDetectedMarkers(frame, corners_o, ids_o)
            rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(corners_o, marker_length_obj, camera_matrix, dist_coeffs)

            if dobot_mode:
                r_o = rvecs[0]
                t_o = tvecs[0].reshape(3, 1)
                R_o, _ = cv2.Rodrigues(r_o)
                t_o = (R_o @ np.array([[0.0, 0.0, -2.2]], dtype=np.float32).T + t_o).flatten()
                t_needle = (np.array([0.0, dobot_offset + needle_length, 0.0], dtype=np.float32) + t_o)

                t_final = R_inv.dot(t_needle - t_c)
                x = t_final[0]
                y = t_final[1] + half_edge
                z = t_final[2]
            else:
                needle_coord = np.array([[0.0, -needle_length, -0.9]], dtype=np.float32)

                r_o = rvecs[0].reshape(3, 1)
                t_o = tvecs[0].reshape(3, 1)
                R_o, _ = cv2.Rodrigues(r_o)

                t_needle = (R_o @ needle_coord.T + t_o).flatten()
                t_final = R_inv.dot(t_needle - t_c)
                x = t_final[0]
                y = t_final[1] + half_edge
                z = t_final[2]

            ### Helper line to labelling
            pts = corners_o[0].reshape(-1, 2)
            cx, cy = pts.mean(axis=0).astype(int)
            h, w = frame.shape[:2]
            cv2.line(frame, (0, cy), (w, cy), (0, 255, 0), 1)

            tip2d, _ = cv2.projectPoints(
                np.array([t_final], dtype=np.float32),
                rvec_c, tvec_c,
                camera_matrix, dist_coeffs
            )
            u, v = tip2d.ravel().astype(int)

            cv2.line(frame, (0, v), (w, v), (0, 255, 0), 1)
            ### Helper line to labelling

            cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, r_o, t_o, axis_length)

            text = f'Position: X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}'
            corner = tuple(corners_o[0][0][0].astype(int))
            cv2.putText(frame, text, (corner[0], corner[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            results.append([frame_idx, round(frame_idx / fps, ndigits=2), x, y, z])
        else:
            results.append([frame_idx, round(frame_idx / fps, ndigits=2), None, None, None])

        cv2.imwrite(f'tracked_frames/frame_{frame_idx}.jpg', frame)
        if not show_video_frame(frame, fps, display):
            break

        frame_idx += 1

    cap.release()
    cv2.destroyAllWindows()
    df = pd.DataFrame(results, columns=['Frame', 'Time (s)', 'Object_X_cm', 'Object_Y_cm', 'Object_Z_cm'])
    return df

def run_aruco_tracking_for_folder(folder_path, cube_mode, dobot_mode, needle_length, starting_position=0.0, marker_length_obj=4.0, fps=30, display=True):
    if not os.path.exists(folder_path):
        print(f"Error: Folder {folder_path} does not exist.")
        return

    video_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.mp4')]
    distances_file_path = os.path.join(folder_path, 'distances.txt')

    if len(video_paths) > 0:
        print(f"Running for videos in {folder_path}: {len(video_paths)} files")

    positions_folder = os.path.join(os.path.dirname(folder_path), 'labelled_positions')
    annotations_folder = os.path.join(os.path.dirname(folder_path), 'annotations')

    for i, video_path in enumerate(
        tqdm(video_paths, desc=f'Folder: {folder_path}', unit='video'),
        start=1
    ):
        tqdm.write(f"Processing ({i}/{len(video_paths)}): {folder_path}")
        if(cube_mode):
            df = track_aruco_cube(video_path, dobot_mode, needle_length, marker_length_obj=marker_length_obj, fps=fps, display=display)
        else:
            df = track_aruco_no_cube(video_path, dobot_mode, needle_length, starting_position=starting_position, marker_length_obj=marker_length_obj, fps=fps, display=display)

        if not df.empty:
            process_data(df, video_path, positions_folder, annotations_folder, distances_file_path, fps=fps)

def process_recursive(root_folder, cube_mode, dobot_mode, needle_length, starting_position=0.0, marker_length_obj=4.0, fps=30, display=True):
    for root, dirs, files in os.walk(root_folder):
        video_files = [f for f in files if f.endswith('.mp4')]
        if video_files:
            print(f"Running for videos in {root}: {len(video_files)} files")
            run_aruco_tracking_for_folder(root, cube_mode, dobot_mode, needle_length, starting_position=starting_position, marker_length_obj=marker_length_obj, fps=fps, display=display)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Tool for annotating position of needle in videos. Can be used to annotate videos in specified folder" \
        "or to annotate videos in every subfolder of specified folder (useful for autonomuos annotating all dataset)." \
        "For each processed video folder, an output folder named 'labelled_positions' will be created at the same level" \
        "as the folder containing the videos. In recursive mode , multiple such output folders will be created." \
        "When you provide distances.txt file in the video folder, it will produce annotations." \
        "distances.txt file should look like: 12,8.5,7,5.4" 
    )
    parser.add_argument("--video-path", required=True, help="Path to folder with videos")
    parser.add_argument("--marker-length", type=float, default=4.0, help="Length of the Aruco marker in cm (default: 4.0 cm)")
    parser.add_argument("--recursive", action="store_true", help="Flag to run recursively in subfolders of video-path (good for annotating all videos in dataset)")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second for video processing (default: 30)")
    parser.add_argument("--display", action="store_true", default=False, help="If true will display tracker on video")
    parser.add_argument("--cube", action="store_true", help="If provided will use cube to detect table grund")
    parser.add_argument("--no-cube", action="store_true", help="If provided will NOT use cube to detect table grund")
    parser.add_argument("--dobot", action="store_true", help="Argument need to be provided if dobot is used during recordings")
    parser.add_argument("--no-dobot", action="store_true", help="Argument need to be provided if dobot is NOT used during recordings")
    parser.add_argument("--needle-length", required=True, type=float, help="Length of whole needle in cm")
    parser.add_argument("--starting-position", default=0.0, type=float, help="Starting position of the needle in cm (default: 0.0 cm). Used only by mode without cube")
    return parser.parse_args()

def main():
    args = parse_args()

    folder_path = args.video_path
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} not found.")
        return

    if not args.cube and not args.no_cube:
        print("Please you have to specify either --cube or --no-cube.")
        return

    if args.cube and args.no_cube:
        print("You cannot specify both --cube and --no-cube.")
        return
    
    if not args.dobot and not args.no_dobot:
        print("Please you have to specify either --dobot or --no-dobot.")
        return
    
    if args.dobot and args.no_dobot:
        print("You cannot specify both --dobot and --no-dobot.")
        return
    
    recursive = args.recursive
    display = args.display
    if(args.cube):
        print("Running in cube mode.")
        cube_mode = True
    elif(args.no_cube):
        print("Running in no-cube mode.")
        cube_mode = False

    if(args.dobot):
        print("Tracking for dobot.")
        dobot_mode = True
    elif(args.no_dobot):
        print("Tracking for no manual.")
        dobot_mode = False

    marker_length_obj = args.marker_length
    fps = args.fps
    needle_length = args.needle_length
    starting_position = args.starting_position
    
    if recursive:
        process_recursive(folder_path, cube_mode, dobot_mode, needle_length, starting_position=starting_position, marker_length_obj=marker_length_obj, fps=fps, display=display)
    else:
        run_aruco_tracking_for_folder(folder_path, cube_mode, dobot_mode, needle_length, starting_position=starting_position, marker_length_obj=marker_length_obj, fps=fps, display=display)

if __name__ == "__main__":
    main()