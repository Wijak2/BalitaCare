from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..extensions import db
from ..models import Anak

children_bp = Blueprint("children", __name__, template_folder="../templates")

@children_bp.route("/children")
def list_anak():
    anak_list = Anak.query.order_by(Anak.id_anak.desc()).all()
    return render_template("list_anak.html", anak_list=anak_list)

@children_bp.route("/children/add", methods=["GET", "POST"])
def add_anak():
    if request.method == "POST":
        nama = request.form["nama"]
        tanggal_lahir = request.form["tanggal_lahir"]
        anak = Anak(nama=nama, tanggal_lahir=tanggal_lahir)
        db.session.add(anak)
        db.session.commit()
        flash("Data anak berhasil ditambahkan!", "success")
        return redirect(url_for("children.list_anak"))
    return render_template("form_anak.html")

@children_bp.route("/children/<int:id_anak>")
def detail_anak(id_anak):
    anak = Anak.query.get_or_404(id_anak)
    return render_template("detail_anak.html", anak=anak)
