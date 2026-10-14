"""
VibraLens · HVSR Calculator
Horizontal-to-Vertical Spectral Ratio (Nakamura, 1989)
"""
import numpy as np
from .preprocess import preprocess
from .spectral import compute_psd, smooth_konno_ohmachi


def compute_hvsr(z, n, e, fs=100,
                 f_min=0.5, f_max=20.0,
                 nperseg=1024, smoothing=True,
                 apply_preprocess=True):
    """
    Hitung kurva HVSR dari 3 komponen sinyal.

    Parameters
    ----------
    z, n, e : ndarray
        Komponen vertikal, north, east
    fs : int
        Sampling rate (Hz)
    f_min, f_max : float
        Rentang frekuensi analisis (Hz)
    nperseg : int
        Panjang window Welch
    smoothing : bool
        Aktifkan smoothing Konno-Ohmachi
    apply_preprocess : bool
        Preprocess (filter, detrend) sebelum analisis

    Returns
    -------
    dict dengan keys:
        frekuensi    : ndarray
        hvsr         : ndarray (kurva HVSR)
        f0           : float (frekuensi dominan, Hz)
        a0           : float (amplifikasi)
        kg           : float (indeks kerentanan Kanai)
        zona         : str
    """
    # Preprocessing
    if apply_preprocess:
        z = preprocess(z, fs=fs)
        n = preprocess(n, fs=fs)
        e = preprocess(e, fs=fs)

    # PSD tiap komponen
    freqs, psd_z = compute_psd(z, fs=fs, nperseg=nperseg)
    _, psd_n = compute_psd(n, fs=fs, nperseg=nperseg)
    _, psd_e = compute_psd(e, fs=fs, nperseg=nperseg)

    # Horizontal = geometric mean (Nakamura standard)
    psd_h = np.sqrt(psd_n * psd_e)

    # HVSR ratio
    with np.errstate(divide='ignore', invalid='ignore'):
        hvsr = np.where(psd_z > 0, psd_h / psd_z, 0)
    hvsr = np.nan_to_num(hvsr, nan=0, posinf=0)

    # Smoothing Konno-Ohmachi
    if smoothing:
        hvsr = smooth_konno_ohmachi(freqs, hvsr, b=40)

    # Batasi range frekuensi
    mask = (freqs >= f_min) & (freqs <= f_max)
    freqs_band = freqs[mask]
    hvsr_band = hvsr[mask]

    if len(hvsr_band) == 0:
        return {
            "frekuensi": [], "hvsr": [],
            "f0": 0, "a0": 0, "kg": 0, "zona": "tidak diketahui",
        }

    # Cari puncak (f0, a0)
    idx_peak = int(np.argmax(hvsr_band))
    f0 = float(freqs_band[idx_peak])
    a0 = float(hvsr_band[idx_peak])

    # Indeks kerentanan Kanai
    kg = float(a0 ** 2 / f0) if f0 > 0 else 0.0

    # Klasifikasi zona
    if kg > 10:
        zona = "rawan"
    elif kg > 3:
        zona = "sedang"
    else:
        zona = "aman"

    return {
        "frekuensi": freqs_band.tolist(),
        "hvsr": hvsr_band.tolist(),
        "f0": round(f0, 3),
        "a0": round(a0, 3),
        "kg": round(kg, 3),
        "zona": zona,
    }


def find_peaks_all(freqs, hvsr, n_peaks=3, min_prominence=0.5):
    """Cari beberapa puncak (kalau ada multi-peak)."""
    from scipy.signal import find_peaks
    peaks, props = find_peaks(hvsr, prominence=min_prominence)
    if len(peaks) == 0:
        return []
    # Urut by prominence (tinggi)
    order = np.argsort(props["prominences"])[::-1][:n_peaks]
    return [
        {
            "f": round(float(freqs[peaks[i]]), 3),
            "amp": round(float(hvsr[peaks[i]]), 3),
        }
        for i in order
    ]