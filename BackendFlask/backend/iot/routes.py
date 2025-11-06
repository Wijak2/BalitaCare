from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from ..extensions import db
from ..models import Pengukuran, Anak, OrangTua, Perawat
from ..analysis.predict import assess_child_growth
from datetime import datetime,date
from ..ai_integration import analyze_with_gemini

iot_bp = Blueprint("iot", __name__, template_folder="../templates")

# -------- VARIABEL GLOBAL UNTUK DATA POST TERBARU --------
latest_data = None


# ==========================================================
# ✅ GUI FORM PENGUKURAN
# ==========================================================
@iot_bp.route("/form", methods=["GET"])
def form_page():
    anak_list = Anak.query.all()
    pengukuran_list = Pengukuran.query.order_by(Pengukuran.id_pengukuran.desc()).all()
    return render_template(
        "form_pengukuran.html",
        anak_list=anak_list,
        pengukuran_list=pengukuran_list
    )


# ==========================================================
# ✅ FORM PENGUKURAN BERTAHAP (Step 1 & Step 2)
# ==========================================================
@iot_bp.route("/form-step1", methods=["GET"])
def form_step1():
    anak_list = Anak.query.all()
    next_id_pengukuran = (db.session.query(db.func.max(Pengukuran.id_pengukuran)).scalar() or 0) + 1
    
    # ✅ Tangkap ID anak dari query parameter
    selected_id = request.args.get("id_anak")

    return render_template(
        "form_pengukuran_step1.html",
        anak_list=anak_list,
        next_id_pengukuran=next_id_pengukuran,
        selected_id=selected_id  # kirim ke template
    )


@iot_bp.route("/form-step2", methods=["POST"])
def form_step2():
    id_anak = request.form.get("id_anak")
    id_pengukuran = request.form.get("id_pengukuran")
    anak = Anak.query.get(id_anak)
    return render_template("form_pengukuran_step2.html",
                           id_anak=id_anak,
                           id_pengukuran=id_pengukuran,
                           anak=anak)

# API: Ambil daftar pengukuran berdasarkan anak
@iot_bp.route("/api/pengukuran-by-anak/<int:id_anak>")
def api_pengukuran_by_anak(id_anak):
    pengukuran = (
        Pengukuran.query.filter_by(id_anak=id_anak)
        .order_by(Pengukuran.created_at.desc())
        .all()
    )
    return jsonify([
        {"id_pengukuran": p.id_pengukuran,
         "tanggal": p.created_at.strftime("%d-%m-%Y") if p.created_at else "-"}
        for p in pengukuran
    ])

# API: Dapatkan ID pengukuran berikutnya
@iot_bp.route("/api/next-id-pengukuran")
def api_next_id_pengukuran():
    next_id = (db.session.query(db.func.max(Pengukuran.id_pengukuran)).scalar() or 0) + 1
    return jsonify({"next_id": next_id})

@iot_bp.route("/api/create-pengukuran", methods=["POST"])
def create_pengukuran():
    id_anak = request.form.get("id_anak") or request.json.get("id_anak")
    tanggal_str = request.form.get("tanggal_pengukuran") or request.json.get("tanggal_pengukuran")

    if not id_anak or not tanggal_str:
        return jsonify({"error": "ID anak dan tanggal wajib dikirim"}), 400

    # ubah string menjadi objek date (tanpa jam)
    tanggal = datetime.strptime(tanggal_str, "%Y-%m-%d").date()

    # 🔍 cek apakah sudah ada pengukuran untuk anak dan tanggal tersebut
    existing = (
        Pengukuran.query
        .filter(
            Pengukuran.id_anak == id_anak,
            db.func.date(Pengukuran.tanggal) == tanggal  # penting: ubah datetime ke date saat query
        )
        .first()
    )

    if existing:
        return jsonify({
            "message": "Pengukuran tanggal ini sudah ada",
            "id_pengukuran": existing.id_pengukuran,
            "tanggal": existing.tanggal.strftime("%Y-%m-%d")
        }), 200

    # kalau belum ada, buat baru
    peng = Pengukuran(
        id_anak=id_anak,
        tanggal=datetime.combine(tanggal, datetime.min.time())  # set jam 00:00 agar konsisten
    )
    db.session.add(peng)
    db.session.commit()

    return jsonify({
        "message": "ID pengukuran baru dibuat",
        "id_pengukuran": peng.id_pengukuran,
        "tanggal": peng.tanggal.strftime("%Y-%m-%d")
    }), 201


# ==========================================================
# ✅ ENDPOINT UNTUK IOT (update nilai sensor)
# ==========================================================
@iot_bp.route("/update/<int:id_pengukuran>", methods=["POST"])
def update_pengukuran_iot(id_pengukuran):
    global latest_data
    data = request.get_json()

    if not data or "nilai" not in data:
        return jsonify({"error": "Format data salah, gunakan { 'nilai': number }"}), 400

    peng = Pengukuran.query.get(id_pengukuran)
    if not peng:
        return jsonify({"error": "Pengukuran tidak ditemukan"}), 404

    # Simpan nilai dari IoT (sementara di lingkar kepala)
    nilai = float(data["nilai"])
    latest_data = {"nilai": nilai}
    peng.lingkar_kepala = nilai
    db.session.commit()

    return jsonify({
        "message": "Data berhasil diterima dari IoT",
        "id_pengukuran": peng.id_pengukuran,
        "latest_data": latest_data
    }), 200


# ==========================================================
# ✅ SIMPAN DATA DARI FORM + IoT KE DATABASE
# ==========================================================
@iot_bp.route("/save-current", methods=["POST"])
def save_current():
    global latest_data
    id_anak = request.form.get("id_anak")
    jenis = request.form.get("jenis")
    id_pengukuran = request.form.get("id_pengukuran")
    tinggi = request.form.get("tinggi_badan")
    berat = request.form.get("berat_badan")

    anak_list = Anak.query.all()
    pengukuran_list = Pengukuran.query.order_by(Pengukuran.id_pengukuran.desc()).all()

    # Cek validitas id_anak
    if not id_anak or id_anak.strip() == "":
        return render_template(
            "form_pengukuran_step2.html",
            anak_list=anak_list,
            pengukuran_list=pengukuran_list,
            error="❌ ID anak tidak ditemukan, silakan kembali ke Langkah 1."
        )

    # ✅ Coba ambil pengukuran berdasarkan ID yang dikirim
    peng = None
    if id_pengukuran and id_pengukuran.strip() != "":
        peng = Pengukuran.query.get(int(id_pengukuran))

    # Kalau tidak ditemukan, buat baru
    if not peng:
        peng = Pengukuran(id_anak=int(id_anak))
        db.session.add(peng)
        db.session.flush()  # flush dulu biar ID-nya langsung muncul

    # ✅ Tangani pengisian data
    if jenis in ["bbtb", "tinggiberat"]:
        # BB & TB bisa tanpa data IoT
        if tinggi:
            peng.tinggi_badan = float(tinggi)
        if berat:
            peng.berat_badan = float(berat)
    else:
        # Pengukuran IoT: lingkar kepala atau lengan
        if not latest_data:
            return render_template(
                "form_pengukuran_step2.html",
                anak_list=anak_list,
                pengukuran_list=pengukuran_list,
                error="❌ Belum ada data IoT yang dikirim.",
                id_anak=id_anak,
                id_pengukuran=id_pengukuran
            )

        nilai = float(latest_data.get("nilai", 0))
        if jenis == "kepala":
            peng.lingkar_kepala = nilai
        elif jenis == "lengan":
            peng.lingkar_lengan = nilai

    db.session.commit()

    return render_template(
        "form_pengukuran_step2.html",
        anak_list=anak_list,
        pengukuran_list=pengukuran_list,
        id_anak=id_anak,
        id_pengukuran=peng.id_pengukuran,
        success=f"✅ Data berhasil disimpan di ID {peng.id_pengukuran}!"
    )



# ==========================================================
# ✅ POST DISPLAY DAN JSON
# ==========================================================
@iot_bp.route("/post-display", methods=["GET", "POST"])
def post_display():
    global latest_data
    if request.method == "POST":
        if request.is_json:
            latest_data = request.get_json()
        else:
            latest_data = request.form.to_dict()
        return jsonify({"message": "Data diterima", "data": latest_data}), 200
    return render_template("post_display.html", data=latest_data)


@iot_bp.route("/latest-json", methods=["GET"])
def latest_json():
    global latest_data
    return jsonify(latest_data if latest_data else {})


# ==========================================================
# ✅ FUNGSI BANTU: HITUNG UMUR DALAM BULAN
# ==========================================================
def hitung_umur_bulan(tanggal_lahir):
    today = datetime.today()
    umur_tahun = today.year - tanggal_lahir.year
    umur_bulan = today.month - tanggal_lahir.month
    total_bulan = umur_tahun * 12 + umur_bulan
    if today.day < tanggal_lahir.day:
        total_bulan -= 1
    return max(0, total_bulan)


# ==========================================================
# ✅ ANALISIS GIZI (dengan model AI)
# ==========================================================
@iot_bp.route("/analyze/<int:id_anak>")
def analyze_anak(id_anak):
    anak = Anak.query.get_or_404(id_anak)
    peng = (
        Pengukuran.query.filter_by(id_anak=id_anak)
        .order_by(Pengukuran.id_pengukuran.desc())
        .first()
    )

    if not peng:
        return jsonify({"error": "Belum ada data pengukuran"}), 400

    umur_bulan = hitung_umur_bulan(anak.tanggal_lahir) if anak.tanggal_lahir else 0

    # Konversi jenis kelamin agar cocok dengan standar WHO
    sex = "Laki-Laki" if anak.jenis_kelamin in ["L", "l", "Laki-Laki"] else "Perempuan"

    hasil = assess_child_growth(
        sex=sex,
        age_months=umur_bulan,
        weight_kg=peng.berat_badan or 0,
        height_cm=peng.tinggi_badan or 1,
        head_circ=peng.lingkar_kepala or 0,
        arm_circ=peng.lingkar_lengan or 0
    )

    return jsonify(hasil)


# ==========================================================
# ✅ DETAIL PENGUKURAN (Integrasi AI ke halaman GUI)
# ==========================================================
@iot_bp.route("/pengukuran/detail/<int:id_anak>")
def detail_pengukuran(id_anak):
    anak = Anak.query.get_or_404(id_anak)
    peng = (
        Pengukuran.query
        .filter_by(id_anak=id_anak)
        .order_by(Pengukuran.created_at.desc(), Pengukuran.id_pengukuran.desc())
        .first()
    )

    if not peng:
        return render_template("detail_pengukuran.html", anak=anak, peng=None, error="Belum ada data pengukuran")

    umur_bulan = hitung_umur_bulan(anak.tanggal_lahir) if anak.tanggal_lahir else 0

    hasil = assess_child_growth(
        sex=anak.jenis_kelamin or "L",
        age_months=umur_bulan,
        weight_kg=peng.berat_badan or 0,
        height_cm=peng.tinggi_badan or 1,
        head_circ=peng.lingkar_kepala or 0,
        arm_circ=peng.lingkar_lengan or 0
    )

    # ==============================
    # 🔹 Siapkan nilai IMT manual (untuk dikirim ke AI)
    imt = peng.berat_badan / ((peng.tinggi_badan / 100) ** 2) if peng.tinggi_badan else None
    # ==============================

    # ======= Integrasi Gemini =======
    prompt = f"""
    Kamu adalah asisten ahli gizi anak.
    Berdasarkan hasil analisis rule-based berikut, berikan interpretasi tambahan tentang perkembangan anak ini,
    apakah perkembangannya baik, area mana yang perlu perhatian, dan saran pemantauan yang sesuai, singkat saja, buat dalam bentuk paragraf

    Data Anak:
    - Nama: {anak.nama}
    - Jenis Kelamin: {anak.jenis_kelamin}
    - Umur: {umur_bulan} bulan
    - Berat Badan: {peng.berat_badan or '-'} kg
    - Tinggi Badan: {peng.tinggi_badan or '-'} cm
    - IMT: {round(imt, 2) if imt else '-'}
    - Lingkar Kepala: {peng.lingkar_kepala or '-'} cm
    - Lingkar Lengan: {peng.lingkar_lengan or '-'} cm

    Hasil Rule-based:
    - BB/U: {hasil.get('BB/U', {}).get('kategori', '-')} (Z-Score: {hasil.get('BB/U', {}).get('z_score', '-')})
    - TB/U: {hasil.get('TB/U', {}).get('kategori', '-')} (Z-Score: {hasil.get('TB/U', {}).get('z_score', '-')})
    - IMT/U: {hasil.get('IMT/U', {}).get('kategori', '-')} (Z-Score: {hasil.get('IMT/U', {}).get('z_score', '-')})
    - LK/U: {hasil.get('LK/U', {}).get('kategori', '-')} (Z-Score: {hasil.get('LK/U', {}).get('z_score', '-')})
    - LILA/U: {hasil.get('LILA/U', {}).get('kategori', '-')} (Z-Score: {hasil.get('LILA/U', {}).get('z_score', '-')})

    Jawab dalam bahasa Indonesia secara singkat, dengan nada ramah dan mudah dipahami orang tua.
    """

    ai_analysis = analyze_with_gemini(prompt)
    # =================================

    return render_template(
        "detail_pengukuran.html",
        anak=anak,
        peng=peng,
        hasil=hasil,
        ai_analysis=ai_analysis,
        umur_bulan=umur_bulan
    )

@iot_bp.route("/api/pengukuran/detail/<int:id_anak>", methods=["GET"])
def api_detail_pengukuran(id_anak):
    try:
        anak = Anak.query.get_or_404(id_anak)
        peng = (
            Pengukuran.query
            .filter_by(id_anak=id_anak)
            .order_by(Pengukuran.created_at.desc(), Pengukuran.id_pengukuran.desc())
            .first()
        )

        if not peng:
            return jsonify({"error": "Belum ada data pengukuran"}), 404

        umur_bulan = hitung_umur_bulan(anak.tanggal_lahir) if anak.tanggal_lahir else 0

        hasil = assess_child_growth(
            sex=anak.jenis_kelamin or "L",
            age_months=umur_bulan,
            weight_kg=peng.berat_badan or 0,
            height_cm=peng.tinggi_badan or 1,
            head_circ=peng.lingkar_kepala or 0,
            arm_circ=peng.lingkar_lengan or 0
        )

        imt = peng.berat_badan / ((peng.tinggi_badan / 100) ** 2) if peng.tinggi_badan else None

        # panggil Gemini AI untuk tambahan analisis
        prompt = f"""
        Kamu adalah asisten ahli gizi anak.
        Berdasarkan hasil analisis rule-based berikut, berikan interpretasi tambahan singkat tentang perkembangan anak ini.

        Data Anak:
        - Nama: {anak.nama}
        - Jenis Kelamin: {anak.jenis_kelamin}
        - Umur: {umur_bulan} bulan
        - Berat Badan: {peng.berat_badan or '-'} kg
        - Tinggi Badan: {peng.tinggi_badan or '-'} cm
        - IMT: {round(imt, 2) if imt else '-'}
        - Lingkar Kepala: {peng.lingkar_kepala or '-'} cm
        - Lingkar Lengan: {peng.lingkar_lengan or '-'} cm

        Hasil Rule-based:
        - BB/U: {hasil.get('BB/U', {}).get('kategori', '-')} (Z-Score: {hasil.get('BB/U', {}).get('z_score', '-')})
        - TB/U: {hasil.get('TB/U', {}).get('kategori', '-')} (Z-Score: {hasil.get('TB/U', {}).get('z_score', '-')})
        - IMT/U: {hasil.get('IMT/U', {}).get('kategori', '-')} (Z-Score: {hasil.get('IMT/U', {}).get('z_score', '-')})
        - LK/U: {hasil.get('LK/U', {}).get('kategori', '-')} (Z-Score: {hasil.get('LK/U', {}).get('z_score', '-')})
        - LILA/U: {hasil.get('LILA/U', {}).get('kategori', '-')} (Z-Score: {hasil.get('LILA/U', {}).get('z_score', '-')})

        Jawab singkat dalam bahasa Indonesia dengan nada ramah dan mudah dipahami.
        """

        ai_analysis = analyze_with_gemini(prompt)

        return jsonify({
            "anak": {
                "id_anak": anak.id_anak,
                "nama": anak.nama,
                "jenis_kelamin": anak.jenis_kelamin,
                "tanggal_lahir": anak.tanggal_lahir.strftime("%Y-%m-%d") if anak.tanggal_lahir else None,
                "umur_bulan": umur_bulan
            },
            "peng": {
                "id_pengukuran": peng.id_pengukuran,
                "berat_badan": peng.berat_badan,
                "tinggi_badan": peng.tinggi_badan,
                "lingkar_kepala": peng.lingkar_kepala,
                "lingkar_lengan": peng.lingkar_lengan,
                "created_at": peng.created_at.strftime("%Y-%m-%d %H:%M:%S") if peng.created_at else None
            },
            "hasil": hasil,
            "imt": round(imt, 2) if imt else None,
            "ai_analysis": ai_analysis
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
# ==========================================================
# ✅ HISTORY DAN GRAFIK
# ==========================================================
@iot_bp.route("/history/<int:id_anak>")
def history_anak(id_anak):
    try:
        data = Pengukuran.query.filter_by(id_anak=id_anak).order_by(Pengukuran.id_pengukuran.desc()).all()
        return render_template("history.html", data=data, id_anak=id_anak)
    except Exception as e:
        print("🔥 ERROR HISTORY:", e)
        return f"Terjadi error: {e}", 500


@iot_bp.route("/history-json/<int:id_anak>")
def history_json(id_anak):
    data = Pengukuran.query.filter_by(id_anak=id_anak).order_by(Pengukuran.created_at.asc()).all()
    result = [
        {
            "tanggal": item.created_at.strftime("%Y-%m-%d"),
            "tinggi": item.tinggi_badan,
            "berat": item.berat_badan
        }
        for item in data
    ]
    return jsonify(result)


@iot_bp.route("/chart/<int:id_anak>")
def chart_anak(id_anak):
    anak = Anak.query.get_or_404(id_anak)
    data = Pengukuran.query.filter_by(id_anak=id_anak).order_by(Pengukuran.created_at.asc()).all()

    tinggi_points = [{"x": p.created_at.strftime("%Y-%m-%d"), "y": p.tinggi_badan} for p in data if p.tinggi_badan]
    berat_points  = [{"x": p.created_at.strftime("%Y-%m-%d"), "y": p.berat_badan} for p in data if p.berat_badan]
    kepala_points = [{"x": p.created_at.strftime("%Y-%m-%d"), "y": p.lingkar_kepala} for p in data if p.lingkar_kepala]
    lengan_points = [{"x": p.created_at.strftime("%Y-%m-%d"), "y": p.lingkar_lengan} for p in data if p.lingkar_lengan]

    return render_template(
        "chart_anak.html",
        anak=anak,
        tinggi_points=tinggi_points,
        berat_points=berat_points,
        kepala_points=kepala_points,
        lengan_points=lengan_points
    )

# ==========================================================
# ✅ API: RIWAYAT PENGUKURAN UNTUK FRONTEND
# ==========================================================
@iot_bp.route("/api/pengukuran/riwayat/<int:id_anak>", methods=["GET"])
def api_pengukuran_riwayat(id_anak):
    try:
        data = Pengukuran.query.filter_by(id_anak=id_anak).order_by(Pengukuran.created_at.desc()).all()
        result = [
            {
                "id_pengukuran": p.id_pengukuran,
                "tanggal": p.tanggal.strftime("%Y-%m-%d") if p.tanggal else None,
                "berat_badan": p.berat_badan,
                "tinggi_badan": p.tinggi_badan,
                "lingkar_kepala": p.lingkar_kepala,
                "lingkar_lengan": p.lingkar_lengan
            }
            for p in data
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ==========================================================
# ✅ CRUD ANAK
# ==========================================================
@iot_bp.route("/anak", methods=["GET"])
def list_anak():
    anak_list = Anak.query.order_by(Anak.id_anak.desc()).all()
    return render_template("list_anak.html", anak_list=anak_list)


@iot_bp.route("/anak/add", methods=["GET", "POST"])
def add_anak():
    if request.method == "POST":
        nama = request.form.get("nama")
        tanggal_lahir = request.form.get("tanggal_lahir")
        jenis_kelamin = request.form.get("jenis_kelamin")

        anak = Anak(
            nama=nama,
            tanggal_lahir=tanggal_lahir,
            jenis_kelamin=jenis_kelamin
        )
        db.session.add(anak)
        db.session.commit()
        return redirect(url_for("iot.list_anak"))
    return render_template("form_anak.html")

@iot_bp.route("/anak/edit/<int:id_anak>", methods=["GET", "POST"])
def edit_anak(id_anak):
    anak = Anak.query.get_or_404(id_anak)
    if request.method == "POST":
        anak.nama = request.form.get("nama")
        anak.tanggal_lahir = request.form.get("tanggal_lahir")
        anak.jenis_kelamin = request.form.get("jenis_kelamin")
        db.session.commit()
        return redirect(url_for("iot.list_anak"))
    return render_template("form_anak.html", anak=anak)

@iot_bp.route("/anak/delete/<int:id_anak>", methods=["POST"])
def delete_anak(id_anak):
    anak = Anak.query.get_or_404(id_anak)
    db.session.delete(anak)
    db.session.commit()
    return redirect(url_for("iot.list_anak"))

@iot_bp.route("/anak/add-by-orangtua/<int:id_orang_tua>", methods=["GET", "POST"])
def add_anak_by_orangtua(id_orang_tua):
    orang_tua = OrangTua.query.get_or_404(id_orang_tua)
    if request.method == "POST":
        nama = request.form.get("nama")
        tanggal_lahir = request.form.get("tanggal_lahir")
        jenis_kelamin = request.form.get("jenis_kelamin")

        anak = Anak(
            nama=nama,
            jenis_kelamin=jenis_kelamin,
            tanggal_lahir=tanggal_lahir,
            id_orang_tua=id_orang_tua
        )
        db.session.add(anak)
        db.session.commit()
        return redirect(url_for("iot.list_anak"))

    return render_template("form_anak.html", orang_tua=orang_tua)

@iot_bp.route("/api/dashboard-stats")
def dashboard_stats():
    # Ambil jumlah dari database
    total_orangtua = db.session.query(OrangTua).count()
    total_anak = db.session.query(Anak).count()
    total_perawat = db.session.query(Perawat).count()

    return jsonify({
        "orangtua": total_orangtua,
        "anak": total_anak,
        "perawat": total_perawat
    })

# route baru untuk dashboard stats
@iot_bp.route("/api/dashboard-stats")
def api_dashboard_stats():
    try:
        count_orangtua = db.session.query(db.func.count(OrangTua.id_orang_tua)).scalar() or 0
        count_anak = db.session.query(db.func.count(Anak.id_anak)).scalar() or 0
        # ganti Perawat.id_perawat sesuai nama kolom di model Perawat
        count_perawat = db.session.query(db.func.count(Perawat.id_perawat)).scalar() or 0

        return jsonify({
            "orangtua": int(count_orangtua),
            "anak": int(count_anak),
            "perawat": int(count_perawat)
        })
    except Exception as e:
        # untuk debugging, kembalikan pesan error (hapus/ubah di production)
        return jsonify({"error": str(e), "orangtua": 0, "anak": 0, "perawat": 0}), 500

# ==========================================================
# ✅ API: DAFTAR ORANG TUA
# ==========================================================
@iot_bp.route("/api/orangtua", methods=["GET"])
def api_orangtua():
    try:
        orangtua_list = OrangTua.query.order_by(OrangTua.id_orang_tua.desc()).all()
        data = [
            {
                "id_orang_tua": o.id_orang_tua,
                "nama": o.nama,
                "email": o.email,
                "telp": o.nomor_hp
            }
            for o in orangtua_list
        ]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ==========================================================
# ✅ API: DAFTAR ANAK BERDASARKAN ORANG TUA
# ==========================================================
@iot_bp.route("/api/anak-by-orangtua/<int:id_orang_tua>", methods=["GET"])
def api_anak_by_orangtua(id_orang_tua):
    try:
        anak_list = Anak.query.filter_by(id_orang_tua=id_orang_tua).order_by(Anak.id_anak.desc()).all()
        data = [
            {
                "id_anak": a.id_anak,
                "nama": a.nama,
                "tanggal_lahir": a.tanggal_lahir.strftime("%Y-%m-%d") if a.tanggal_lahir else "-",
                "jenis_kelamin": a.jenis_kelamin,   # ✅ tambahkan ini
                "status": "Terdaftar"
            }
            for a in anak_list
        ]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================================
# ✅ API: DAFTAR SEMUA ANAK (JSON)
# ==========================================================
@iot_bp.route("/api/anak", methods=["GET"])
def api_anak():
    try:
        anak_list = Anak.query.order_by(Anak.id_anak.desc()).all()
        data = [
            {
                "id_anak": a.id_anak,
                "nama": a.nama,
                "tanggal_lahir": a.tanggal_lahir.strftime("%Y-%m-%d") if a.tanggal_lahir else "-",
                "jenis_kelamin": a.jenis_kelamin,
                "id_orang_tua": a.id_orang_tua
            }
            for a in anak_list
        ]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@iot_bp.route("/api/anak/<int:id_anak>", methods=["GET"])
def api_get_anak(id_anak):
    anak = Anak.query.get_or_404(id_anak)
    return jsonify({
        "id_anak": anak.id_anak,
        "nama": anak.nama,
        "jenis_kelamin": anak.jenis_kelamin,
        "tanggal_lahir": anak.tanggal_lahir.strftime("%Y-%m-%d") if anak.tanggal_lahir else None,
        "id_orang_tua": anak.id_orang_tua
    })
