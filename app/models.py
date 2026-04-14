from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False, default="user")  # user or superadmin
    is_subscription_active = db.Column(db.Boolean, default=True)
    is_active_user = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    playlists = db.relationship("Playlist", backref="owner", lazy=True, cascade="all, delete-orphan")
    songs = db.relationship("Song", backref="owner", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<User {self.username}>"

class Song(db.Model):
    __tablename__ = "songs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    artist_name = db.Column(db.String(150), nullable=False)
    album_name = db.Column(db.String(150), nullable=True)
    language = db.Column(db.String(50), nullable=True)
    genre = db.Column(db.String(50), nullable=True)

    release_date = db.Column(db.Date, nullable=True)
    release_year = db.Column(db.Integer, nullable=True)

    movie_name = db.Column(db.String(150), nullable=True)
    is_movie_song = db.Column(db.Boolean, default=False)
    is_private_album = db.Column(db.Boolean, default=False)

    singer_gender = db.Column(db.String(20), nullable=True)  # male / female / duet
    duration = db.Column(db.String(20), nullable=True)

    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    mime_type = db.Column(db.String(100), nullable=True)

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    playlist_links = db.relationship("PlaylistSong", backref="song", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Song {self.title}>"

class Playlist(db.Model):
    __tablename__ = "playlists"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    playlist_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_auto_generated = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    songs = db.relationship("PlaylistSong", backref="playlist", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Playlist {self.playlist_name}>"

class PlaylistSong(db.Model):
    __tablename__ = "playlist_songs"

    id = db.Column(db.Integer, primary_key=True)

    playlist_id = db.Column(db.Integer, db.ForeignKey("playlists.id"), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey("songs.id"), nullable=False)

    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("playlist_id", "song_id", name="unique_playlist_song"),
    )

    def __repr__(self):
        return f"<PlaylistSong playlist_id={self.playlist_id} song_id={self.song_id}>"

class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="reset_tokens")

    def __repr__(self):
        return f"<PasswordResetToken user_id={self.user_id}>"

class SubscriptionLog(db.Model):
    __tablename__ = "subscription_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # deactivated / reactivated
    action_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    remarks = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", foreign_keys=[user_id], backref="subscription_actions")
    admin_user = db.relationship("User", foreign_keys=[action_by])

    def __repr__(self):
        return f"<SubscriptionLog user_id={self.user_id} action={self.action_type}>"

class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="activity_logs")

    def __repr__(self):
        return f"<ActivityLog action={self.action}>"