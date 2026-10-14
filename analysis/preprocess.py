"""
VibraLens · Preprocessing sinyal
Detrend, bandpass filter, windowing — standar SESAME guidelines.
"""
import numpy as np
from scipy import signal


def detrend(sinyal):
    """Hilangkan DC offset / trend linear."""
    return signal.detrend(sinyal, type='linear')


def bandpass_filter(sinyal, fs=100, f_low=0.1, f_high=20.0, order=4):
    """
    Bandpass filter Butterworth.
    Default 0.1–20 Hz → standar ambient noise HVSR.
    """
    nyq = fs / 2.0
    low = max(f_low / nyq, 0.001)
    high = min(f_high / nyq, 0.999)
    sos = signal.butter(order, [low, high], btype='band', output='sos')
    return signal.sosfiltfilt(sos, sinyal)


def remove_mean(sinyal):
    """Hilangkan nilai rata-rata."""
    return sinyal - np.mean(sinyal)


def preprocess(sinyal, fs=100, f_low=0.1, f_high=20.0):
    """
    Pipeline preprocessing lengkap:
    1. Remove mean
    2. Detrend linear
    3. Bandpass filter
    """
    x = np.asarray(sinyal, dtype=float)
    x = remove_mean(x)
    x = detrend(x)
    x = bandpass_filter(x, fs=fs, f_low=f_low, f_high=f_high)
    return x


def split_windows(sinyal, fs=100, window_sec=30, overlap=0.5):
    """
    Bagi sinyal panjang jadi window-window pendek.
    Default 30 detik per window, 50% overlap.
    """
    n_win = int(window_sec * fs)
    step = int(n_win * (1 - overlap))
    windows = []
    for start in range(0, len(sinyal) - n_win + 1, step):
        windows.append(sinyal[start:start + n_win])
    return windows