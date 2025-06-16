import gdown
import os

gdown.download(
    "https://drive.google.com/uc?id=1dRyy8ar81iSZshwz9yWInNtckmtXDhud",
    "goturn.caffemodel",
    quiet=False
)

gdown.download(
    "https://drive.google.com/uc?id=1uwy0Rp8wFfRA7YTeOnMnkdThdaEcqOO7",
    "goturn.prototxt",
    quiet=False
)