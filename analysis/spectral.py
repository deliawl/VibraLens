"""
VibraLens · Spectral analysis
Power Spectral Density (PSD) via Welch method.
"""
import numpy as np
from scipy import signal


def compute_psd(sinyal, fs=100, nperseg=1024, noverlap=None, window='hann'):
    """
    Hitung Power Spectral Density pakai Welch method.

    Returns
    -------
    freqs : ndarray
        Array frekuensi (Hz)
    psd : ndarray
        Power Spectral Density
    """
    if noverlap is None:
        noverlap = nperseg // 2

    freqs, psd = signal.welch(
        sinyal,
        fs=fs,
        nperseg=min(nperseg, len(sinyal)),
        noverlap=min(noverlap, len(sinyal) // 2),
        window=window,
        detrend='linear',
        scaling='density',
    )
    return freqs, psd


def compute_fft(sinyal, fs=100):
    """FFT satu sisi (untuk spektrogram sederhana)."""
    n = len(sinyal)
    fft_vals = np.fft.rfft(sinyal)
    freqs = np.fft.rfftfreq(n, 1/fs)
    magnitude = np.abs(fft_vals) / n
    return freqs, magnitude


def smooth_konno_ohmachi(freqs, psd, b=40):
    """
    Smoothing Konno-Ohmachi (standar HVSR).
    B = 40 (default), makin besar makin halus.
    """
    freqs = np.asarray(freqs)
    psd = np.asarray(psd)
    out = np.zeros_like(psd)

    for i, f0 in enumerate(freqs):
        if f0 <= 0:
            out[i] = psd[i]
            continue
        # Log-spaced window
        ratio = freqs / f0
        log_ratio = np.log10(ratio)
        # Hindari log(0)
        with np.errstate(divide='ignore', invalid='ignore'):
            w = np.where(
                ratio > 0,
                (np.sin(b * log_ratio) / (b * log_ratio)) ** 4,
                0,
            )
        w = np.nan_to_num(w, nan=1.0, posinf=1.0)
        # Weighted average
        num = np.sum(w * psd)
        den = np.sum(w)
        out[i] = num / den if den > 0 else psd[i]

    return out