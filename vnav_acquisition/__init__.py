import gdown
import os

if not os.path.exists("goturn.caffemodel"):
    gdown.download(
        "https://drive.google.com/uc?id=1dRyy8ar81iSZshwz9yWInNtckmtXDhud",
        "goturn.caffemodel",
        quiet=False
    )

if not os.path.exists("goturn.prototxt"):
    gdown.download(
        "https://drive.google.com/uc?id=1uwy0Rp8wFfRA7YTeOnMnkdThdaEcqOO7",
        "goturn.prototxt",
        quiet=False
    )