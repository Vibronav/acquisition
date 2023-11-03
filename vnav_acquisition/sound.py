import numpy as np
import sounddevice as sd


def generate_chirp_signal(duration, start_freq, end_freq, sample_rate):
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    chirp_signal = np.sin(2 * np.pi * np.interp(t, [0, duration], [start_freq, end_freq]) * t)
    return chirp_signal


def play_chirp_signal():
    sd.play(_chirp_signal, 44100)


_chirp_signal = generate_chirp_signal(duration=0.2, start_freq=500, end_freq=4000, sample_rate=44100)