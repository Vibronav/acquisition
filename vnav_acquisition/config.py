import json


class Configurator:
    _DEFAULT_CONFIG = {
        'connection': ["192.168.0.110", 22, "pi", "VibroNav"],
        'materials': ["Slime", "Silicone", "PU", "Plato (play dough)", "Plastic", "Ikea (plastic bag)",
                      "African (silk)"],
        'speeds': ["slow", "medium", "fast"],
        'local_dir': "micro_data",
        'remote_dir': "vnav_acquisition"
    }

    def __init__(self):
        self._config = dict()

    def load_from_json(self, path):
        with open(path) as f:
            self._config = json.load(f)

    def __getitem__(self, key):
        return self._config.get(key, self._DEFAULT_CONFIG[key])


config = Configurator()
