import glob
import os
import json
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, required=True)
    args = parser.parse_args()

    for json_file in glob.glob(os.path.join(args.path, "*.json")):
        with open(json_file) as f:
            annotation = json.load(f)
        video_annotations = annotation.get("video_annotations")
        if video_annotations is not None and type(video_annotations) is list:
            annotation["video_annotations"] = video_annotations[0]
            with open(json_file, 'w') as f:
                json.dump(annotation, f)
            print(f"Fixed {os.path.basename(json_file)}")


if __name__ == "__main__":
    main()
