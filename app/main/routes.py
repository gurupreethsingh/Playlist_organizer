from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from app.models import Song

# ✅ THIS WAS MISSING
main_bp = Blueprint("main", __name__)


# =========================
# HOME PAGE
# =========================
@main_bp.route("/")
def home():
    return render_template("main/home.html")


@main_bp.route("/about")
def about():
    return render_template("main/about.html")


# =========================
# DASHBOARD (SMART STATS)
# =========================
@main_bp.route("/dashboard")
@login_required
def dashboard():
    songs = Song.query.filter_by(user_id=current_user.id).all()

    stats = {
        "total_songs": len(songs),
        "languages": len(set([s.language for s in songs if s.language])),
        "genres": len(set([s.genre for s in songs if s.genre])),
        "artists": len(set([s.artist_name for s in songs if s.artist_name])),
        "years": len(set([s.release_year for s in songs if s.release_year])),
    }

    return render_template("user/dashboard.html", stats=stats)


# =========================
# CATEGORY FILTER PAGE
# =========================
@main_bp.route("/category/<type>/<value>")
@login_required
def category_songs(type, value):
    query = Song.query.filter_by(user_id=current_user.id)

    if type == "language":
        query = query.filter(Song.language == value)
    elif type == "genre":
        query = query.filter(Song.genre == value)
    elif type == "artist":
        query = query.filter(Song.artist_name == value)
    elif type == "year":
        query = query.filter(Song.release_year == int(value))
    elif type == "movie":
        query = query.filter(Song.is_movie_song == True)
    elif type == "private":
        query = query.filter(Song.is_private_album == True)

    songs = query.all()

    return render_template(
        "user/category_songs.html",
        songs=songs,
        type=type,
        value=value
    )