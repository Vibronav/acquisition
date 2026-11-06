import argparse
import json
from pathlib import Path
import shutil

import cv2
import pandas as pd


def copy_to_fix(video_path, second_video_folder, audio_folder):
    sources = [
        (video_path, "tofix_video_cam1"),
        (Path(second_video_folder) / video_path.name, "tofix_video_cam2"),
        (Path(audio_folder) / f"{video_path.stem}.wav", "tofix_audio_raw"),
    ]
    for source, folder_name in sources:
        destination = source.parent.parent / folder_name
        destination.mkdir(exist_ok=True)
        shutil.copy2(source, destination / source.name)
    print(f"Copied {video_path.stem} to tofix folders.")


def main():
    parser = argparse.ArgumentParser(description="Browse annotated video frames and needle positions.")
    parser.add_argument("--video-path", required=True)
    parser.add_argument("--second-video-path", required=True)
    parser.add_argument("--audio-path", required=True)
    parser.add_argument("--annotations-path", required=True)
    parser.add_argument("--positions-path", required=True)
    args = parser.parse_args()

    items = []
    for video_path in sorted(Path(args.video_path).glob("*.mp4")):
        annotation_path = Path(args.annotations_path) / f"{video_path.stem}.json"
        positions_path = Path(args.positions_path) / f"{video_path.stem}.csv"
        if not annotation_path.is_file() or not positions_path.is_file():
            print(f"Skipping {video_path.name}: missing {annotation_path} or {positions_path}")
            continue
        with open(annotation_path) as file:
            annotations = json.load(file)["video_annotations"]
        positions = pd.read_csv(positions_path).set_index("Frame")

        for number, annotation in sorted(annotations.items(), key=lambda item: int(item[0])):
            position = positions.loc[int(annotation["frame"])]
            items.append((video_path, number, annotation, position))

    if not items:
        print("No annotations to display.")
        return

    index = 0
    playing = False
    cv2.namedWindow("Annotations", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Annotations", 1600, 1000)

    while True:
        video_path, number, annotation, position = items[index]
        frame_number = int(annotation["frame"])
        cap = cv2.VideoCapture(str(video_path))
        # track_position numbers frames from 1; OpenCV seeks from 0.
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)
        _, frame = cap.read()
        cap.release()

        frame = cv2.copyMakeBorder(
            frame, 130, 0, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0)
        )
        lines = [
            video_path.name,
            f"Annotation: {number} | Frame: {frame_number} | Time: {annotation['time']:.3f} s",
            f"Needle [cm]: X={position['Object_X_cm']:.2f}  "
            f"Y={position['Object_Y_cm']:.2f}  Z={position['Object_Z_cm']:.2f}",
            f"{index + 1}/{len(items)} | {'PLAY' if playing else 'PAUSE'} | "
            "Space: play/pause | A: previous | D: next | F: copy to fix | Esc: exit",
        ]
        for line_index, text in enumerate(lines):
            cv2.putText(
                frame, text, (10, 25 + line_index * 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA
            )
        cv2.imshow("Annotations", frame)

        key = cv2.waitKey(1000 if playing else 0) & 0xFF
        if key == 27:
            break
        elif key == ord(" "):
            playing = not playing
        elif key == ord("a"):
            index = max(0, index - 1)
            playing = False
        elif key == ord("d"):
            index = min(len(items) - 1, index + 1)
            playing = False
        elif key == ord("f"):
            copy_to_fix(video_path, args.second_video_path, args.audio_path)
        elif key == 255 and playing:
            if index < len(items) - 1:
                index += 1
            else:
                playing = False

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
