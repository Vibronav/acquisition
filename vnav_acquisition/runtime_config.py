

class RuntimeConfig:
    _DEFAULT_CONFIG = {
        'micro_output': None,
        'micro_bandpass_enabled': True,
        'micro_bandpass_low': 4000,
        'micro_bandpass_high': 6000,
    }

    def __init__(self):
        self._config = dict()

    def set_value(self, key, value):
        self._config[key] = value

    def __getitem__(self, key):
        return self._config.get(key, self._DEFAULT_CONFIG[key])


runtime_config = RuntimeConfig()
