from flask import Flask
from flask_cors import CORS
from backend.extensions import db
from backend.auth.routes import auth_bp
from backend.iot.routes import iot_bp
from dotenv import load_dotenv
import os
import sys

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

if not SECRET_KEY:
    sys.exit("❌ ERROR: SECRET_KEY tidak ditemukan di file .env")
if not DATABASE_URL:
    sys.exit("❌ ERROR: DATABASE_URL tidak ditemukan di file .env")

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
CORS(app, supports_credentials=True, origins=[FRONTEND_URL])

db.init_app(app)
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(iot_bp, url_prefix="/iot")

if __name__ == "__main__":
    debug_mode = os.getenv("DEBUG", "True").lower() == "true"
    app.run(debug=debug_mode)
