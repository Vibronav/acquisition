import json
from flask import jsonify


class Configurator:
    _DEFAULT_CONFIG = {
        "username": "",
        "connection": ["raspberrypi.local", 22, "pi", "VibroNav"],
        "defaultMaterials": [
            "Slime",
            "Silicone",
            "PU",
            "Plato (play dough)",
            "Plastic",
            "Ikea (plastic bag)",
            "African (silk)"
        ],
        "chosenMaterials": [],
        "newMaterials": [],
        "defaultSpeeds": ["slow", "medium", "fast"],
        "chosenSpeeds": [],
        "newSpeeds": [],
        "local_dir": "c:\\vnav_acquisition",
        "remote_dir": "vnav_acquisition",
        "lab_checks": [
            "Quiet room/reduce external noises",
            "Background white Screen",
            "Camera angle",
            "Microphone locations/connections",
            "Material/User/speed info",
            "Test recordings",
            "Gained signal check"
        ],
        "chosen_lab_checks": [
            "Quiet room/reduce external noises",
            "Background white Screen",
            "Camera angle",
            "Microphone locations/connections",
            "Material/User/speed info",
            "Test recordings",
            "Gained signal check"
        ],
        "new_lab_checks": []
    }

    def __init__(self):
        self._config = self._DEFAULT_CONFIG

    def load_from_json(self, path):
        with open(path) as f:
            self._config = json.load(f)

    def __getitem__(self, key):
        return self._config.get(key, self._DEFAULT_CONFIG[key])


config = Configurator()


