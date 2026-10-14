"""
VibraLens · AI Interpretation (Rule-Based Expert System)

Sistem pakar berbasis aturan untuk interpretasi hasil HVSR.
Aturan disusun berdasarkan:
  - Nakamura (1989) — HVSR method
  - Kanai (1983) — Vulnerability Index
  - SESAME (2004) — HVSR Guidelines
  - Referensi lokal: Irsyam dkk. (2017) — Peta Gempa Indonesia

Filosofi: deterministic, transparan, bisa dijelaskan step-by-step.
"""


def klasifikasi_frekuensi(f0):
    """Klasifikasi berdasarkan frekuensi dominan (Hz)."""
    if f0 < 1.0:
        return {
            "kategori": "sangat_rendah",
            "label": "Frekuensi dominan sangat rendah",
            "deskripsi": "Sedimen sangat tebal (>30 m), umumnya cekungan atau dataran alluvial",
            "implikasi": "Rentan terhadap gempa periode panjang (gempa jauh & besar)",
        }
    elif f0 < 2.5:
        return {
            "kategori": "rendah",
            "label": "Frekuensi dominan rendah",
            "deskripsi": "Sedimen tebal (15–30 m)",
            "implikasi": "Berpotensi amplifikasi getaran sedang–tinggi",
        }
    elif f0 < 5.0:
        return {
            "kategori": "sedang",
            "label": "Frekuensi dominan sedang",
            "deskripsi": "Sedimen sedang (5–15 m)",
            "implikasi": "Respons tanah moderat terhadap goncangan",
        }
    elif f0 < 10.0:
        return {
            "kategori": "tinggi",
            "label": "Frekuensi dominan tinggi",
            "deskripsi": "Sedimen tipis (<5 m) atau batuan lapuk",
            "implikasi": "Respons tanah relatif kaku, amplifikasi rendah",
        }
    else:
        return {
            "kategori": "sangat_tinggi",
            "label": "Frekuensi dominan sangat tinggi",
            "deskripsi": "Batuan keras / bedrock",
            "implikasi": "Amplifikasi minimal, tanah stabil",
        }


def klasifikasi_amplifikasi(a0):
    """Klasifikasi berdasarkan faktor amplifikasi (rasio H/V)."""
    if a0 < 2.0:
        return {
            "kategori": "rendah",
            "label": "Amplifikasi rendah",
            "deskripsi": "Kontras impedansi kecil antara sedimen dan bedrock",
            "implikasi": "Perkuatan getaran minimal",
        }
    elif a0 < 4.0:
        return {
            "kategori": "sedang",
            "label": "Amplifikasi sedang",
            "deskripsi": "Kontras impedansi moderat",
            "implikasi": "Getaran diperkuat 2–4× dari bedrock ke permukaan",
        }
    elif a0 < 6.0:
        return {
            "kategori": "tinggi",
            "label": "Amplifikasi tinggi",
            "deskripsi": "Kontras impedansi besar",
            "implikasi": "Getaran diperkuat signifikan, perlu perhatian",
        }
    else:
        return {
            "kategori": "sangat_tinggi",
            "label": "Amplifikasi sangat tinggi",
            "deskripsi": "Kontras impedansi sangat besar, potensi resonansi kuat",
            "implikasi": "Zona prioritas mitigasi — rawan amplifikasi gempa",
        }


def klasifikasi_kerentanan(kg):
    """Klasifikasi berdasarkan indeks kerentanan seismik Kanai."""
    if kg < 3.0:
        return {
            "zona": "aman",
            "label": "Zona Aman",
            "warna": "hijau",
            "deskripsi": "Tanah stabil, kerentanan rendah",
            "rekomendasi": "Monitoring rutin, tidak perlu intervensi khusus",
        }
    elif kg < 10.0:
        return {
            "zona": "sedang",
            "label": "Zona Sedang",
            "warna": "kuning",
            "deskripsi": "Kerentanan moderat terhadap amplifikasi gempa",
            "rekomendasi": "Perlu monitoring lebih intensif & evaluasi struktur bangunan",
        }
    else:
        return {
            "zona": "rawan",
            "label": "Zona Rawan",
            "warna": "merah",
            "deskripsi": "Kerentanan tinggi, potensi amplifikasi besar",
            "rekomendasi": "Prioritas mitigasi — pertimbangkan retrofit bangunan & kajian geoteknik lanjutan",
        }


def estimasi_kedalaman_sedimen(f0, vs_avg=200):
    """
    Estimasi kedalaman sedimen pakai rumus H ≈ Vs / (4 * f0)
    (asumsi quarter-wavelength, Nakamura).

    vs_avg: kecepatan gelombang S rata-rata (m/s). Default 200 m/s
            (tipikal sedimen lunak).
    """
    if f0 <= 0:
        return None
    h = vs_avg / (4 * f0)
    return round(h, 1)


def interpret_hvsr(f0, a0, kg, node_info=None):
    """
    Hasilkan interpretasi lengkap dari parameter HVSR.

    Returns
    -------
    dict dengan:
        ringkasan  : str (1 paragraf)
        kategori   : dict (per aspek)
        narasi     : list[str] (poin-poin)
        rekomendasi: str
        confidence : str
    """
    freq_cls = klasifikasi_frekuensi(f0)
    amp_cls = klasifikasi_amplifikasi(a0)
    vul_cls = klasifikasi_kerentanan(kg)
    kedalaman = estimasi_kedalaman_sedimen(f0)

    # === Ringkasan ===
    lokasi_str = f"Node {node_info['nama']}" if node_info else "Lokasi ini"
    ringkasan = (
        f"{lokasi_str} memiliki frekuensi dominan f₀ = {f0:.2f} Hz "
        f"dengan faktor amplifikasi A₀ = {a0:.2f}×. "
        f"Berdasarkan indeks kerentanan Kanai (K_g = {kg:.2f}), "
        f"lokasi ini tergolong dalam {vul_cls['label'].lower()}. "
        f"{freq_cls['deskripsi']}."
    )

    # === Narasi poin-poin ===
    narasi = [
        f"**Frekuensi Dominan ({f0:.2f} Hz)** — {freq_cls['label']}. {freq_cls['deskripsi']}.",
        f"**Amplifikasi ({a0:.2f}×)** — {amp_cls['label']}. {amp_cls['implikasi']}.",
        f"**Indeks Kerentanan ({kg:.2f})** — {vul_cls['label']}. {vul_cls['deskripsi']}.",
    ]

    if kedalaman:
        narasi.append(
            f"**Estimasi Kedalaman Sedimen** — sekitar {kedalaman} m "
            f"(asumsi Vs rata-rata 200 m/s, rumus Nakamura)."
        )

    # === Analisis korelasi f0–A0–Kg ===
    if f0 < 2.5 and a0 > 4.0:
        narasi.append(
            "⚠️ **Kombinasi berbahaya**: f₀ rendah + A₀ tinggi → amplifikasi besar "
            "pada frekuensi yang berpotensi beresonansi dengan bangunan bertingkat rendah–sedang."
        )
    elif f0 > 5.0 and a0 < 3.0:
        narasi.append(
            "✅ **Kondisi ideal**: batuan dasar relatif keras, amplifikasi minimal, "
            "tanah stabil untuk berbagai jenis bangunan."
        )

    # === Rekomendasi ===
    rekomendasi = vul_cls["rekomendasi"]
    if vul_cls["zona"] == "rawan":
        rekomendasi += ". Disarankan kajian mikrotremor lanjutan dengan durasi lebih panjang (>60 menit) untuk konfirmasi."
    elif vul_cls["zona"] == "sedang":
        rekomendasi += ". Pemantauan berkala setiap 6 bulan direkomendasikan."

    # === Confidence level ===
    # (untuk data sintetis selalu tinggi, untuk data real tergantung SNR)
    confidence = "tinggi" if 0.5 <= f0 <= 15 else "sedang"

    return {
        "ringkasan": ringkasan,
        "kategori": {
            "frekuensi": freq_cls,
            "amplifikasi": amp_cls,
            "kerentanan": vul_cls,
        },
        "narasi": narasi,
        "rekomendasi": rekomendasi,
        "kedalaman_estimasi": kedalaman,
        "confidence": confidence,
        "referensi": [
            "Nakamura, Y. (1989). A method for dynamic characteristics estimation of subsurface using microtremor on the ground surface.",
            "Kanai, K. (1983). Engineering Seismology. University of Tokyo Press.",
            "SESAME (2004). Guidelines for the implementation of the H/V spectral ratio technique.",
        ],
    }