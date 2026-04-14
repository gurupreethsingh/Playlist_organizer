from sqlalchemy import func
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.decorators import active_subscription_required, subscribed_user_required
from app.extensions import db
from app.models import Playlist, PlaylistSong, Song
from app.user import __name__ as user_module_name

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/dashboard")
@login_required
@subscribed_user_required
def dashboard():
    total_playlists = Playlist.query.filter_by(user_id=current_user.id).count()
    total_uploaded_songs = Song.query.filter_by(user_id=current_user.id).count()

    total_songs_in_playlists = (
        db.session.query(func.count(PlaylistSong.id))
        .join(Playlist, Playlist.id == PlaylistSong.playlist_id)
        .filter(Playlist.user_id == current_user.id)
        .scalar()
        or 0
    )

    total_languages = (
        db.session.query(func.count(func.distinct(Song.language)))
        .filter(Song.user_id == current_user.id, Song.language.isnot(None), Song.language != "")
        .scalar()
        or 0
    )

    total_genres = (
        db.session.query(func.count(func.distinct(Song.genre)))
        .filter(Song.user_id == current_user.id, Song.genre.isnot(None), Song.genre != "")
        .scalar()
        or 0
    )

    total_artists = (
        db.session.query(func.count(func.distinct(Song.artist_name)))
        .filter(Song.user_id == current_user.id, Song.artist_name.isnot(None), Song.artist_name != "")
        .scalar()
        or 0
    )

    movie_song_count = Song.query.filter_by(user_id=current_user.id, is_movie_song=True).count()
    private_album_count = Song.query.filter_by(user_id=current_user.id, is_private_album=True).count()

    recent_songs = (
        Song.query.filter_by(user_id=current_user.id)
        .order_by(Song.uploaded_at.desc())
        .limit(5)
        .all()
    )

    recent_playlists = (
        Playlist.query.filter_by(user_id=current_user.id)
        .order_by(Playlist.created_at.desc())
        .limit(5)
        .all()
    )

    language_breakdown = (
        db.session.query(Song.language, func.count(Song.id))
        .filter(Song.user_id == current_user.id, Song.language.isnot(None), Song.language != "")
        .group_by(Song.language)
        .order_by(func.count(Song.id).desc())
        .limit(6)
        .all()
    )

    genre_breakdown = (
        db.session.query(Song.genre, func.count(Song.id))
        .filter(Song.user_id == current_user.id, Song.genre.isnot(None), Song.genre != "")
        .group_by(Song.genre)
        .order_by(func.count(Song.id).desc())
        .limit(6)
        .all()
    )

    singer_breakdown = (
        db.session.query(Song.singer_gender, func.count(Song.id))
        .filter(Song.user_id == current_user.id, Song.singer_gender.isnot(None), Song.singer_gender != "")
        .group_by(Song.singer_gender)
        .order_by(func.count(Song.id).desc())
        .all()
    )

    return render_template(
        "user/dashboard.html",
        total_playlists=total_playlists,
        total_uploaded_songs=total_uploaded_songs,
        total_songs_in_playlists=total_songs_in_playlists,
        total_languages=total_languages,
        total_genres=total_genres,
        total_artists=total_artists,
        movie_song_count=movie_song_count,
        private_album_count=private_album_count,
        recent_songs=recent_songs,
        recent_playlists=recent_playlists,
        language_breakdown=language_breakdown,
        genre_breakdown=genre_breakdown,
        singer_breakdown=singer_breakdown,
    )


@user_bp.route("/subscription-status")
@login_required
@subscribed_user_required
def subscription_status():
    return render_template("user/subscription_status.html")