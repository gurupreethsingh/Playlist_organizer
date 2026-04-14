import os

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.decorators import active_subscription_required
from app.extensions import db
from app.forms import SongEditForm, SongUploadForm
from app.models import Song
from app.utils import allowed_audio_file, delete_file_if_exists, generate_unique_filename

songs_bp = Blueprint("songs", __name__, url_prefix="/songs")


@songs_bp.route("/my-songs")
@login_required
@active_subscription_required
def my_songs():
    search = request.args.get("search", "").strip()
    language = request.args.get("language", "").strip()
    genre = request.args.get("genre", "").strip()

    query = Song.query.filter_by(user_id=current_user.id)

    if search:
        query = query.filter(
            db.or_(
                Song.title.ilike(f"%{search}%"),
                Song.artist_name.ilike(f"%{search}%"),
                Song.album_name.ilike(f"%{search}%"),
                Song.movie_name.ilike(f"%{search}%"),
            )
        )

    if language:
        query = query.filter(Song.language == language)

    if genre:
        query = query.filter(Song.genre == genre)

    songs = query.order_by(Song.uploaded_at.desc()).all()

    languages = (
        db.session.query(Song.language)
        .filter(
            Song.user_id == current_user.id,
            Song.language.isnot(None),
            Song.language != "",
        )
        .distinct()
        .order_by(Song.language.asc())
        .all()
    )
    languages = [item[0] for item in languages]

    genres = (
        db.session.query(Song.genre)
        .filter(
            Song.user_id == current_user.id,
            Song.genre.isnot(None),
            Song.genre != "",
        )
        .distinct()
        .order_by(Song.genre.asc())
        .all()
    )
    genres = [item[0] for item in genres]

    return render_template(
        "songs/my_songs.html",
        songs=songs,
        search=search,
        selected_language=language,
        selected_genre=genre,
        languages=languages,
        genres=genres,
    )


@songs_bp.route("/upload", methods=["GET", "POST"])
@login_required
@active_subscription_required
def upload_song():
    form = SongUploadForm()

    if form.validate_on_submit():
        uploaded_file = form.audio_file.data

        if not uploaded_file:
            flash("Please select an MP3 file.", "danger")
            return render_template("songs/upload_song.html", form=form)

        filename = uploaded_file.filename or ""
        if not allowed_audio_file(filename, current_app.config["ALLOWED_AUDIO_EXTENSIONS"]):
            flash("Only MP3 files are allowed.", "danger")
            return render_template("songs/upload_song.html", form=form)

        unique_filename = generate_unique_filename(filename)
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_filename)

        uploaded_file.save(save_path)

        file_size = None
        try:
            file_size = os.path.getsize(save_path)
        except OSError:
            file_size = None

        release_date_value = form.release_date.data
        release_year_value = release_date_value.year if release_date_value else None

        new_song = Song(
            user_id=current_user.id,
            title=form.title.data.strip(),
            artist_name=form.artist_name.data.strip(),
            album_name=form.album_name.data.strip() if form.album_name.data else None,
            language=form.language.data if form.language.data else None,
            genre=form.genre.data if form.genre.data else None,
            release_date=release_date_value,
            release_year=release_year_value,
            movie_name=form.movie_name.data.strip() if form.movie_name.data else None,
            is_movie_song=form.is_movie_song.data,
            is_private_album=form.is_private_album.data,
            singer_gender=form.singer_gender.data if form.singer_gender.data else None,
            duration=form.duration.data.strip() if form.duration.data else None,
            file_name=unique_filename,
            file_path=save_path,
            file_size=file_size,
            mime_type="audio/mpeg",
        )

        db.session.add(new_song)
        db.session.commit()

        flash("Song uploaded successfully.", "success")
        return redirect(url_for("songs.my_songs"))

    return render_template("songs/upload_song.html", form=form)


@songs_bp.route("/<int:song_id>")
@login_required
@active_subscription_required
def song_detail(song_id):
    song = Song.query.filter_by(id=song_id, user_id=current_user.id).first_or_404()
    return render_template("songs/song_detail.html", song=song)


@songs_bp.route("/<int:song_id>/edit", methods=["GET", "POST"])
@login_required
@active_subscription_required
def edit_song(song_id):
    song = Song.query.filter_by(id=song_id, user_id=current_user.id).first_or_404()
    form = SongEditForm(obj=song)

    if request.method == "GET":
        form.release_date.data = song.release_date

    if form.validate_on_submit():
        song.title = form.title.data.strip()
        song.artist_name = form.artist_name.data.strip()
        song.album_name = form.album_name.data.strip() if form.album_name.data else None
        song.language = form.language.data if form.language.data else None
        song.genre = form.genre.data if form.genre.data else None
        song.release_date = form.release_date.data
        song.release_year = form.release_date.data.year if form.release_date.data else None
        song.movie_name = form.movie_name.data.strip() if form.movie_name.data else None
        song.is_movie_song = form.is_movie_song.data
        song.is_private_album = form.is_private_album.data
        song.singer_gender = form.singer_gender.data if form.singer_gender.data else None
        song.duration = form.duration.data.strip() if form.duration.data else None

        db.session.commit()

        flash("Song details updated successfully.", "success")
        return redirect(url_for("songs.song_detail", song_id=song.id))

    return render_template("songs/edit_song.html", form=form, song=song)


@songs_bp.route("/<int:song_id>/delete", methods=["POST"])
@login_required
@active_subscription_required
def delete_song(song_id):
    song = Song.query.filter_by(id=song_id, user_id=current_user.id).first_or_404()

    file_path = song.file_path

    db.session.delete(song)
    db.session.commit()

    delete_file_if_exists(file_path)

    flash("Song deleted successfully.", "success")
    return redirect(url_for("songs.my_songs"))