from flask import Flask, render_template, jsonify, request
from database import init_db, DB_PATH
import queries as q
from env_api import get_env_for_node

app = Flask(__name__)

if not DB_PATH.exists():
    init_db()
    print("\n⚠️  Database baru dibuat TAPI kosong.")
    print("    Jalankan: python seed.py\n")


FITUR = {
    "monitoring":  {"nama_id": "Monitoring Real-Time", "nama_en": "Real-Time Monitoring", "ikon": "activity"},
    "event":       {"nama_id": "Event & Alarm",        "nama_en": "Events & Alarms",      "ikon": "siren"},
    "analisis":    {"nama_id": "Analisis Sinyal",      "nama_en": "Signal Analysis",      "ikon": "audio-waveform"},
    "katalog":     {"nama_id": "Katalog Data",         "nama_en": "Data Catalog",         "ikon": "database"},
    "peta":        {"nama_id": "Peta & Jaringan",      "nama_en": "Map & Network",        "ikon": "network"},
    "riwayat":     {"nama_id": "Riwayat & Ekspor",     "nama_en": "History & Export",     "ikon": "history"},
    "pengaturan":  {"nama_id": "Pengaturan Sistem",    "nama_en": "System Settings",      "ikon": "sliders-horizontal"},
}


# ============================================================
# Context processor
# ============================================================
@app.context_processor
def inject_stats():
    stats = q.get_sistem_stats()
    stats["pgv_series"] = q.get_pgv_series(hours=24, limit=24)
    stats["node_hvsr"] = q.get_hvsr_per_node()
    stats["hvsr_curve"] = q.get_hvsr_curve_rata()
    return {"stats": stats}


# ============================================================
# Halaman
# ============================================================
@app.route("/")
def beranda():
    return render_template("index.html", fitur=FITUR, show_time=False, active=None)


@app.route("/katalog")
def katalog():
    nodes = q.get_all_nodes()
    return render_template("katalog.html", fitur=FITUR, active="katalog",
                           show_time=False, nodes=nodes)


@app.route("/katalog/<node_id>")
def katalog_detail(node_id):
    node = q.get_node(node_id)
    if not node:
        return "Node tidak ditemukan", 404
    return render_template("katalog_detail.html", fitur=FITUR, active="katalog",
                           show_time=False, node=node)


@app.route("/fitur/<slug>")
def fitur_page(slug):
    if slug not in FITUR:
        return "Fitur tidak ditemukan", 404

    meta = FITUR[slug]

    # Katalog punya route sendiri
    if slug == "katalog":
        return katalog()

    # Peta
    if slug == "peta":
        nodes = q.get_active_nodes()
        return render_template(
            "fitur/peta.html",
            fitur=FITUR, active=slug, show_time=True,
            meta=meta, slug=slug, nodes=nodes,
        )

    # Analisis
    if slug == "analisis":
        nodes = q.get_active_nodes()
        return render_template(
            "fitur/analisis.html",
            fitur=FITUR, active=slug, show_time=True,
            meta=meta, slug=slug, nodes=nodes,
        )

    # Event & Alarm
    if slug == "event":
        events = q.get_events_extended(limit=200)
        summary = q.get_event_summary()
        nodes = q.get_active_nodes()
        return render_template(
            "fitur/event.html",
            fitur=FITUR, active=slug, show_time=True,
            meta=meta, slug=slug,
            events=events, summary=summary, nodes=nodes,
        )

    # Monitoring Real-Time
    if slug == "monitoring":
        nodes = q.get_active_nodes()
        stats = q.get_sistem_stats()
        stats["pgv_series"] = q.get_pgv_series(hours=6, limit=72)
        return render_template(
            "fitur/monitoring.html",
            fitur=FITUR, active=slug, show_time=True,
            meta=meta, slug=slug, nodes=nodes, stats=stats,
        )

    # Riwayat & Ekspor
    if slug == "riwayat":
        nodes = q.get_all_nodes()
        readings = q.get_readings_filtered(limit=100)
        return render_template(
            "fitur/riwayat.html",
            fitur=FITUR, active=slug, show_time=True,
            meta=meta, slug=slug,
            nodes=nodes, readings=readings,
        )

    # Pengaturan
    if slug == "pengaturan":
        info = q.get_system_info()
        return render_template(
            "fitur/pengaturan.html",
            fitur=FITUR, active=slug, show_time=True,
            meta=meta, slug=slug, info=info,
        )

    return render_template(
        "fitur/placeholder.html",
        fitur=FITUR, active=slug, show_time=True,
        meta=meta, slug=slug,
    )

# ============================================================
# Halaman Bantuan
# ============================================================
@app.route("/panduan")
def panduan():
    return render_template("bantuan/panduan.html", fitur=FITUR,
                           active=None, show_time=False)


@app.route("/glosarium")
def glosarium():
    return render_template("bantuan/glosarium.html", fitur=FITUR,
                           active=None, show_time=False)


@app.route("/referensi")
def referensi():
    return render_template("bantuan/referensi.html", fitur=FITUR,
                           active=None, show_time=False)

# ============================================================
# API · Nodes
# ============================================================
@app.route("/api/nodes")
def api_nodes():
    from datetime import datetime
    nodes = q.get_all_nodes()
    return jsonify({
        "updated_at": datetime.now().isoformat(),
        "nodes": nodes,
    })


@app.route("/api/nodes/<node_id>")
def api_node(node_id):
    node = q.get_node(node_id)
    if not node:
        return jsonify({"error": "Node tidak ditemukan"}), 404
    return jsonify(node)


@app.route("/api/nodes/<node_id>/readings")
def api_readings(node_id):
    hours = int(request.args.get("hours", 24))
    data = q.get_readings(node_id, hours=hours)
    return jsonify({
        "node_id": node_id,
        "hours": hours,
        "count": len(data),
        "readings": data,
    })


@app.route("/api/nodes/<node_id>/hvsr")
def api_hvsr(node_id):
    data = q.get_latest_hvsr(node_id)
    if not data:
        return jsonify({"error": "Belum ada data HVSR"}), 404
    return jsonify(data)


# ============================================================
# API · Env (NASA POWER)
# ============================================================
@app.route("/api/nodes/<node_id>/env")
def api_env_node(node_id):
    """Data lingkungan untuk 1 node (auto-fetch kalau cache expired)."""
    node = q.get_node(node_id)
    if not node:
        return jsonify({"error": "Node tidak ditemukan"}), 404

    lat = node["lokasi"]["latitude"]
    lon = node["lokasi"]["longitude"]
    force = request.args.get("refresh") == "1"

    env = get_env_for_node(node_id, lat, lon, force=force)
    if not env:
        return jsonify({"error": "Data tidak tersedia"}), 503
    return jsonify(env)


@app.route("/api/env/<node_id>")
def api_env(node_id):
    """Alias endpoint env."""
    return api_env_node(node_id)


# ============================================================
# API · Events
# ============================================================
@app.route("/api/events")
def api_events():
    node_id = request.args.get("node_id")
    limit = int(request.args.get("limit", 50))
    return jsonify({"events": q.get_events(node_id, limit)})


@app.route("/api/events/filter")
def api_events_filter():
    node_id = request.args.get("node_id")
    tipe = request.args.get("tipe")
    limit = int(request.args.get("limit", 200))
    return jsonify({
        "events": q.get_events_extended(node_id, tipe, limit),
        "summary": q.get_event_summary(),
    })


# ============================================================
# API · Stats
# ============================================================
@app.route("/api/stats")
def api_stats():
    stats = q.get_sistem_stats()
    stats["pgv_series"] = q.get_pgv_series(hours=24, limit=24)
    return jsonify(stats)


# ============================================================
# API · Analysis (HVSR)
# ============================================================
@app.route("/api/analysis/<node_id>")
def api_analysis(node_id):
    """Jalankan pipeline HVSR untuk 1 node."""
    duration = int(request.args.get("duration", 1800))
    result = q.run_hvsr_analysis(node_id, duration=duration)
    if not result:
        return jsonify({"error": "Node tidak ditemukan"}), 404
    return jsonify(result)


@app.route("/api/analysis/<node_id>/raw")
def api_analysis_raw(node_id):
    """Ambil waveform mentah (untuk debug/visualisasi)."""
    wf = q.get_waveform_for_node(node_id, duration=60)
    if not wf:
        return jsonify({"error": "Node tidak ditemukan"}), 404

    # Downsample biar JSON nggak terlalu besar
    step = max(1, len(wf["z"]) // 2000)
    return jsonify({
        "node_id": node_id,
        "fs": wf["fs"],
        "duration": wf["duration"],
        "samples": len(wf["z"]),
        "downsample": step,
        "z": wf["z"][::step].tolist(),
        "n": wf["n"][::step].tolist(),
        "e": wf["e"][::step].tolist(),
    })


# ============================================================
# API · Readings Filter & Export
# ============================================================
@app.route("/api/readings/filter")
def api_readings_filter():
    node_id = request.args.get("node_id")
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    limit = int(request.args.get("limit", 1000))
    return jsonify({
        "readings": q.get_readings_filtered(node_id, date_from, date_to, limit),
        "count": len(q.get_readings_filtered(node_id, date_from, date_to, limit)),
    })


@app.route("/api/export/<node_id>.csv")
def api_export_csv(node_id):
    """Export readings node ke CSV."""
    import csv
    import io
    from flask import Response

    date_from = request.args.get("from")
    date_to = request.args.get("to")
    rows = q.get_readings_filtered(node_id, date_from, date_to, limit=10000)

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "timestamp", "node_id", "pgv_mm_s", "pga_ms2", "freq_dom_hz",
        "rms", "kanal_1", "kanal_2", "kanal_3",
        "curah_hujan_mm", "kelembaban_pct", "suhu_c", "tekanan_hpa", "status"
    ])

    for r in rows:
        writer.writerow([
            r.get("timestamp"), r.get("node_id"), r.get("pgv"), r.get("pga"),
            r.get("freq_dom"), r.get("rms"),
            r.get("kanal_1"), r.get("kanal_2"), r.get("kanal_3"),
            r.get("curah_hujan"), r.get("kelembaban"),
            r.get("suhu"), r.get("tekanan"), r.get("status"),
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=vibralens_{node_id}.csv"
        },
    )


@app.route("/api/system/info")
def api_system_info():
    return jsonify(q.get_system_info())


# ============================================================
# Error handlers
# ============================================================
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", fitur=FITUR, active=None, show_time=False), 404


# ============================================================
# Startup: warmup env cache
# ============================================================
def warmup_env_cache():
    """Fetch env data kalau cache expired (silent fail)."""
    try:
        from env_api import is_cache_valid
        nodes = q.get_all_nodes()
        for n in nodes:
            if not is_cache_valid(n["id"]):
                get_env_for_node(
                    n["id"],
                    n["lokasi"]["latitude"],
                    n["lokasi"]["longitude"]
                )
    except Exception as e:
        print(f"[Warmup] Skip: {e}")


if __name__ == "__main__":
    import os
    debug_mode = os.environ.get("FLASK_ENV") != "production"

    warmup_env_cache()
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)