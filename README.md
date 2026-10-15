# VibraLens

Sistem pemantauan getaran tanah real-time berbasis IoT dengan analisis HVSR untuk microzonasi seismik di kawasan Universitas Padjadjaran Jatinangor.

Project ini dibuat sebagai bagian dari skripsi Program Studi Geofisika, Universitas Padjadjaran.

---

## Tentang Project

VibraLens adalah sistem terintegrasi yang menggabungkan tiga komponen utama:

1. Perangkat IoT ground recorder (geophone 3-komponen + LoRa)
2. Pipeline pengolahan sinyal seismik berbasis metode HVSR
3. Dashboard web untuk pemantauan dan analisis

Kawasan Unpad Jatinangor berada dalam radius pengaruh Sesar Cimandiri sekitar 30 km, sehingga karakterisasi dinamis tanah penting untuk mitigasi risiko gempa.

Parameter yang diestimasi:

- f0 = frekuensi dominan (Hz), terkait ketebalan sedimen
- A0 = faktor amplifikasi, terkait kontras impedansi
- K_g = indeks kerentanan seismik, dihitung dari K_g = A0^2 / f0

Interpretasi hasil analisis dilakukan otomatis oleh sistem pakar berbasis aturan, disusun dari Nakamura (1989), Kanai (1983), dan SESAME (2004).

---

## Fitur

- Beranda dengan ringkasan sistem dan statistik real-time
- Monitoring real-time dengan auto-refresh tiap 5 detik
- Analisis HVSR otomatis plus interpretasi AI
- Peta interaktif dengan marker status node
- Katalog metadata lengkap semua node
- Log event dan alarm
- Riwayat data dengan export CSV
- Pengaturan sistem dan threshold
- Halaman bantuan: panduan, glosarium, referensi
- Dark mode dan light mode
- Multi-bahasa (Indonesia dan English)
- Integrasi data lingkungan dari NASA POWER

---

## Teknologi

Backend:
- Python 3.11, Flask 3.0.3, SQLite
- NumPy 1.26.4 dan SciPy 1.13.1 untuk pengolahan sinyal
- Gunicorn 22.0.0 untuk production server

Frontend:
- HTML, CSS, JavaScript (vanilla)
- Leaflet.js 1.9.4, Lucide Icons, Google Fonts

Deployment:
- Docker dan Docker Compose

---

## Instalasi Singkat

```bash
git clone https://github.com/USERNAME/VibraLens.git
cd VibraLens
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows
source venv/bin/activate            # macOS/Linux
python -m pip install -r requirements.txt
python seed.py --force
python app.py

Buka http://localhost:5000

Untuk panduan lengkap, lihat folder docs/.