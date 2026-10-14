"""
VibraLens · Waveform synthesizer
Generate sinyal dummy yang menyerupai data geophone real.

Setiap node punya karakteristik HVSR (f0, a0) — generator ini
bikin sinyal yang kalau di-HVSR-process, hasilnya mendekati
parameter target tersebut.

CATATAN: Modul ini HANYA untuk demo/testing. Nanti kalau data
sensor real sudah tersedia, tinggal ganti sumber di queries.py.
"""
import numpy as np
from datetime import datetime, timezone


def generate_waveform(f0=4.0, a0=3.0, duration=1800, fs=100, seed=None):
    """
    Generate 3-komponen waveform sintetis dengan karakteristik HVSR.

    Parameters
    ----------
    f0 : float
        Frekuensi dominan target (Hz)
    a0 : float
        Amplifikasi target (rasio H/V puncak)
    duration : int
        Durasi sinyal (detik). Default 1800 (30 menit).
    fs : int
        Sampling rate (Hz). Default 100.
    seed : int or None
        Random seed untuk reproducibility.

    Returns
    -------
    dict dengan keys:
        z  : ndarray (vertikal)
        n  : ndarray (north)
        e  : ndarray (east)
        fs : int
        duration : int
    """
    if seed is None:
        seed = hash(f"{f0}-{a0}") % (2**31)

    rng = np.random.default_rng(seed)
    n_samples = int(duration * fs)

    # Frekuensi domain
    freqs = np.fft.rfftfreq(n_samples, 1/fs)
    df = freqs[1] - freqs[0] if len(freqs) > 1 else 1.0

    # ---- Base ambient noise (1/f-like, pink noise approximation) ----
    # Hindari pembagian nol di frekuensi 0
    f_safe = np.where(freqs > 0.01, freqs, 0.01)
    base_psd = 1.0 / (1.0 + f_safe) ** 1.2

    # ---- Peak Gaussian di f0 ----
    peak_width = max(0.3, f0 * 0.15)
    gaussian = np.exp(-((freqs - f0) ** 2) / (2 * peak_width ** 2))

    # Vertikal: peak kecil (0.3× dari horizontal)
    psd_z = base_psd + 0.3 * gaussian
    # Horizontal: peak besar (sesuai a0)
    psd_h = base_psd + a0 * gaussian

    # ---- Random phase ----
    phase_z = rng.uniform(0, 2 * np.pi, len(freqs))
    phase_n = rng.uniform(0, 2 * np.pi, len(freqs))
    phase_e = rng.uniform(0, 2 * np.pi, len(freqs))

    # ---- Kompleks spektrum ----
    spec_z = np.sqrt(psd_z) * np.exp(1j * phase_z)
    spec_n = np.sqrt(psd_h) * np.exp(1j * phase_n)
    spec_e = np.sqrt(psd_h) * np.exp(1j * phase_e)

    # ---- IFFT ke time domain ----
    z = np.fft.irfft(spec_z, n_samples)
    n = np.fft.irfft(spec_n, n_samples)
    e = np.fft.irfft(spec_e, n_samples)

    # ---- Normalize supaya PGV realistis (0.1–1.5 mm/s) ----
    target_pgv = 0.05 + 0.15 * a0  # makin tinggi a0, makin besar amplitudo
    max_val = max(np.abs(z).max(), np.abs(n).max(), np.abs(e).max())
    if max_val > 0:
        scale = target_pgv / max_val
        z *= scale
        n *= scale
        e *= scale

    return {
        "z": z,
        "n": n,
        "e": e,
        "fs": fs,
        "duration": duration,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }