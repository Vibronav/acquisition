

class RuntimeConfig:
    _DEFAULT_CONFIG = {
        'micro_output': 0 
    }

    def __init__(self):
        self._config = dict()

    def set_value(self, key, value):
        self._config[key] = value

    def __getitem__(self, key):
        return self._config.get(key, self._DEFAULT_CONFIG[key])


runtime_config = RuntimeConfig()
