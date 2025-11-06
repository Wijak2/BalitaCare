from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import jwt

from ..extensions import db
from ..models import OrangTua, Perawat

auth_bp = Blueprint("auth", __name__)
SECRET_KEY = "YOUR_SECRET_KEY"  # ganti dengan yang kuat


# ============================================================
# ✅ Helper: generate token JWT
# ============================================================
def generate_token(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=7),   # token valid 7 hari
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


# ============================================================
# ✅ Register Orang Tua
# ============================================================
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    nama = data.get("nama")
    password = data.get("password")
    no_hp = data.get("no_hp")
    email = data.get("email")

    if OrangTua.query.filter(
        (OrangTua.nomor_hp == no_hp) | (OrangTua.email == email)
    ).first():
        return jsonify({"error": "Nomor HP atau email sudah terdaftar!"}), 400

    orangtua = OrangTua(
        nama=nama,
        nomor_hp=no_hp,
        email=email or f"{no_hp}@dummy.local",
        password=generate_password_hash(password)
    )

    db.session.add(orangtua)
    db.session.commit()

    return jsonify({"message": "Registrasi berhasil!"}), 201


# ============================================================
# ✅ Login (orang tua & perawat)
# ============================================================
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    identifier = data.get("identifier")
    password = data.get("password")

    orangtua_user = OrangTua.query.filter(
        (OrangTua.nomor_hp == identifier) | (OrangTua.email == identifier)
    ).first()

    perawat_user = Perawat.query.filter(
        (Perawat.email == identifier) | (Perawat.nomor_hp == identifier)
    ).first()


    user = None
    role = None

    if orangtua_user and check_password_hash(orangtua_user.password, password):
        user = orangtua_user
        role = "orang_tua"

    elif perawat_user and check_password_hash(perawat_user.password, password):
        user = perawat_user
        role = "perawat"

    if not user:
        return jsonify({"error": "Email/No HP atau password salah!"}), 401

    user_id = getattr(user, "id_orang_tua", None) or getattr(user, "id_perawat", None)

    # ✅ generate JWT
    token = generate_token(user_id, role)

    return jsonify({
        "message": "Login berhasil!",
        "token": token,
        "role": role,
        "user_id": user_id
    }), 200


# ============================================================
# ✅ Middleware: cek token JWT
# ============================================================
def require_token(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401

        token = auth_header.split(" ")[1]

        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        request.user = decoded  # berisi user_id dan role
        return f(*args, **kwargs)

    return decorated


# ============================================================
# ✅ Contoh endpoint dilindungi token
# ============================================================
@auth_bp.route("/whoami", methods=["GET"])
@require_token
def whoami():
    return jsonify({
        "user_id": request.user["user_id"],
        "role": request.user["role"]
    })
