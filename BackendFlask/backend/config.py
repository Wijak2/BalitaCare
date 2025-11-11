import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ============================================================
    # 🔹 Basic configuration
    # ============================================================
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ============================================================
    # 🔹 Database configuration (MySQL + PyMySQL)
    # ============================================================
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME")

    if all([DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME]):
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    else:
        SQLALCHEMY_DATABASE_URI = None
        print("⚠️  WARNING: Database environment variables are incomplete. Check .env file.")

    # ============================================================
    # 🔹 Gemini API configuration
    # ============================================================
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-2.5-flash"
    GEMINI_THINKING_BUDGET = 0
