from flask import Blueprint, render_template, redirect, url_for, flash, request
from ..models import Anak, OrangTua, Pengukuran
from ..extensions import db

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard", template_folder="../templates")

# --- DASHBOARD ADMIN ---
@dashboard_bp.route("/admin")
def admin_dashboard():
    anak_list = Anak.query.all()
    orangtua_list = OrangTua.query.all()
    pengukuran_list = Pengukuran.query.all()
    return render_template(
        "dashboard_admin.html",
        anak_list=anak_list,
        orangtua_list=orangtua_list,
        pengukuran_list=pengukuran_list
    )

# --- DASHBOARD ORANG TUA ---
@dashboard_bp.route("/orangtua/<int:id_orang_tua>")
def orangtua_dashboard(id_orang_tua):
    anak_list = Anak.query.filter_by(id_orang_tua=id_orang_tua).all()
    return render_template("dashboard_orangtua.html", anak_list=anak_list)

# --- CRUD ANAK UNTUK ORANG TUA ---
@dashboard_bp.route("/anak/add", methods=["GET", "POST"])
def add_anak():
    if request.method == "POST":
        nama = request.form["nama"]
        id_orang_tua = request.form["id_orang_tua"]
        tanggal_lahir = request.form.get("tanggal_lahir")

        anak = Anak(nama=nama, id_orang_tua=id_orang_tua, tanggal_lahir=tanggal_lahir)
        db.session.add(anak)
        db.session.commit()
        flash("Anak berhasil ditambahkan!", "success")
        return redirect(url_for("dashboard.orangtua_dashboard", id_orang_tua=id_orang_tua))
    return render_template("anak_crud.html", action="add")

@dashboard_bp.route("/anak/delete/<int:id_anak>")
def delete_anak(id_anak):
    anak = Anak.query.get_or_404(id_anak)
    id_orang_tua = anak.id_orang_tua
    db.session.delete(anak)
    db.session.commit()
    flash("Data anak berhasil dihapus!", "info")
    return redirect(url_for("dashboard.orangtua_dashboard", id_orang_tua=id_orang_tua))
