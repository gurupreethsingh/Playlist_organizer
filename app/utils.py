# utility helpers will be added in the next stepimport os
import secrets
from datetime import datetime, timedelta
from uuid import uuid4

from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import PasswordResetToken


def allowed_audio_file(filename, allowed_extensions):
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in allowed_extensions


def generate_unique_filename(filename):
    safe_name = secure_filename(filename)
    unique_prefix = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_suffix = uuid4().hex[:10]
    return f"{unique_prefix}_{random_suffix}_{safe_name}"


def save_password_reset_token(user, expiry_minutes=30):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at,
        used=False,
    )

    db.session.add(reset_token)
    db.session.commit()

    return reset_token


def get_valid_password_reset_token(token_value):
    token_record = PasswordResetToken.query.filter_by(token=token_value, used=False).first()

    if not token_record:
        return None

    if token_record.expires_at < datetime.utcnow():
        return None

    return token_record


def mark_password_reset_token_used(token_record):
    token_record.used = True
    db.session.commit()


def delete_file_if_exists(file_path):
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass