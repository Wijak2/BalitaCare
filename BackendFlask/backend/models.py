from datetime import datetime
from .extensions import db

# ========================
# Model Orang Tua
# ========================
class OrangTua(db.Model):
    __tablename__ = "orang_tua"

    id_orang_tua = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nomor_hp = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    anak = db.relationship("Anak", backref="orang_tua", lazy=True)

    def __repr__(self):
        return f"<OrangTua {self.id_orang_tua} - {self.nama}>"


# ========================
# Model Perawat / Admin
# ========================
class Perawat(db.Model):
    __tablename__ = "perawat"

    id_perawat = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nomor_hp = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Perawat {self.id_perawat} - {self.nama}>"


# ========================
# Model Anak
# ========================
class Anak(db.Model):
    __tablename__ = "anak"

    id_anak = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_orang_tua = db.Column(db.Integer, db.ForeignKey("orang_tua.id_orang_tua"), nullable=True)
    nama = db.Column(db.String(100), nullable=False)
    jenis_kelamin = db.Column(db.Enum('Laki-laki', 'Perempuan'), nullable=True)
    tanggal_lahir = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pengukuran = db.relationship("Pengukuran", backref="anak", lazy=True)

    def __repr__(self):
        return f"<Anak {self.id_anak} - {self.nama}>"


# ========================
# Model Pengukuran
# ========================
class Pengukuran(db.Model):
    __tablename__ = "pengukuran"

    id_pengukuran = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_anak = db.Column(db.Integer, db.ForeignKey("anak.id_anak"), nullable=False)
    id_perawat = db.Column(db.Integer, db.ForeignKey("perawat.id_perawat"), nullable=True)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    lingkar_kepala = db.Column(db.Float, nullable=True)
    lingkar_lengan = db.Column(db.Float, nullable=True)
    tinggi_badan = db.Column(db.Float, nullable=True)
    berat_badan = db.Column(db.Float, nullable=True)
    z_bb = db.Column(db.Float, nullable=True)
    kategori_bb = db.Column(db.String(50), nullable=True)
    z_tb = db.Column(db.Float, nullable=True)
    kategori_tb = db.Column(db.String(50), nullable=True)
    z_lk = db.Column(db.Float, nullable=True)
    kategori_lk = db.Column(db.String(50), nullable=True)
    z_imt = db.Column(db.Float, nullable=True)
    kategori_imt = db.Column(db.String(50), nullable=True)
    z_lila = db.Column(db.Float, nullable=True)
    kategori_lila = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Pengukuran {self.id_pengukuran} - Anak {self.id_anak}>"
