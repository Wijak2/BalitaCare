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
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

if not SECRET_KEY:
    sys.exit("❌ ERROR: SECRET_KEY tidak ditemukan di file .env")
if not all([DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME]):
    sys.exit("❌ ERROR: Variabel DB_USERNAME, DB_PASSWORD, DB_HOST, atau DB_NAME tidak ditemukan di file .env")

app = Flask(__name__)
app.secret_key = SECRET_KEY
DATABASE_URI = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app, supports_credentials=True)

db.init_app(app)
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(iot_bp, url_prefix="/iot")

if __name__ == "__main__":
    debug_mode = os.getenv("DEBUG", "True").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0")
