import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "super-secret-key-change-this-in-production"

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads", "songs")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max upload size

    ALLOWED_AUDIO_EXTENSIONS = {"mp3"}

    RESET_TOKEN_EXPIRY_MINUTES = 30