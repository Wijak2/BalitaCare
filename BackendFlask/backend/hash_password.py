from werkzeug.security import generate_password_hash
from backend.extensions import db
from backend.models import Perawat, OrangTua
from backend import create_app  # pastikan kamu punya factory app

app = create_app()
with app.app_context():
    # Hash semua password perawat
    perawats = Perawat.query.all()
    for p in perawats:
        if not p.password.startswith("pbkdf2:sha256"):
            p.password = generate_password_hash(p.password)
    db.session.commit()

    # Hash semua password orang tua (jika ada)
    orangtuas = OrangTua.query.all()
    for o in orangtuas:
        if not o.password.startswith("pbkdf2:sha256"):
            o.password = generate_password_hash(o.password)
    db.session.commit()

    print("✅ Semua password berhasil di-hash!")
