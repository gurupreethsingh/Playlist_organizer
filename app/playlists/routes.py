from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.decorators import active_subscription_required
from app.extensions import db
from app.forms import PlaylistForm
from app.models import Playlist, PlaylistSong, Song

playlists_bp = Blueprint("playlists", __name__, url_prefix="/playlists")


@playlists_bp.route("/")
@login_required
@active_subscription_required
def my_playlists():
    search = request.args.get("search", "").strip()

    query = Playlist.query.filter_by(user_id=current_user.id)

    if search:
        query = query.filter(Playlist.playlist_name.ilike(f"%{search}%"))

    playlists = query.order_by(Playlist.created_at.desc()).all()

    playlist_song_counts = {}
    if playlists:
        playlist_ids = [playlist.id for playlist in playlists]
        counts = (
            db.session.query(PlaylistSong.playlist_id, db.func.count(PlaylistSong.id))
            .filter(PlaylistSong.playlist_id.in_(playlist_ids))
            .group_by(PlaylistSong.playlist_id)
            .all()
        )
        playlist_song_counts = {playlist_id: count for playlist_id, count in counts}

    return render_template(
        "playlists/my_playlists.html",
        playlists=playlists,
        search=search,
        playlist_song_counts=playlist_song_counts,
    )


@playlists_bp.route("/create", methods=["GET", "POST"])
@login_required
@active_subscription_required
def create_playlist():
    form = PlaylistForm()

    if form.validate_on_submit():
        playlist = Playlist(
            user_id=current_user.id,
            playlist_name=form.playlist_name.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            is_auto_generated=False,
        )

        db.session.add(playlist)
        db.session.commit()

        flash("Playlist created successfully.", "success")
        return redirect(url_for("playlists.my_playlists"))

    return render_template("playlists/create_playlist.html", form=form)


@playlists_bp.route("/<int:playlist_id>")
@login_required
@active_subscription_required
def playlist_detail(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first_or_404()

    playlist_song_links = (
        PlaylistSong.query.filter_by(playlist_id=playlist.id)
        .join(Song, Song.id == PlaylistSong.song_id)
        .order_by(PlaylistSong.added_at.desc())
        .all()
    )

    return render_template(
        "playlists/playlist_detail.html",
        playlist=playlist,
        playlist_song_links=playlist_song_links,
    )


@playlists_bp.route("/<int:playlist_id>/edit", methods=["GET", "POST"])
@login_required
@active_subscription_required
def edit_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first_or_404()
    form = PlaylistForm(obj=playlist)

    if form.validate_on_submit():
        playlist.playlist_name = form.playlist_name.data.strip()
        playlist.description = form.description.data.strip() if form.description.data else None

        db.session.commit()

        flash("Playlist updated successfully.", "success")
        return redirect(url_for("playlists.playlist_detail", playlist_id=playlist.id))

    return render_template("playlists/edit_playlist.html", form=form, playlist=playlist)


@playlists_bp.route("/<int:playlist_id>/delete", methods=["POST"])
@login_required
@active_subscription_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first_or_404()

    db.session.delete(playlist)
    db.session.commit()

    flash("Playlist deleted successfully.", "success")
    return redirect(url_for("playlists.my_playlists"))


@playlists_bp.route("/<int:playlist_id>/add-songs", methods=["GET", "POST"])
@login_required
@active_subscription_required
def add_songs_to_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first_or_404()

    existing_song_ids = [
        row.song_id for row in PlaylistSong.query.filter_by(playlist_id=playlist.id).all()
    ]

    search = request.args.get("search", "").strip()

    query = Song.query.filter_by(user_id=current_user.id)

    if search:
        query = query.filter(
            db.or_(
                Song.title.ilike(f"%{search}%"),
                Song.artist_name.ilike(f"%{search}%"),
                Song.album_name.ilike(f"%{search}%"),
            )
        )

    available_songs = query.order_by(Song.uploaded_at.desc()).all()

    if request.method == "POST":
        selected_song_ids = request.form.getlist("song_ids")

        if not selected_song_ids:
            flash("Please select at least one song to add.", "warning")
            return render_template(
                "playlists/add_songs_to_playlist.html",
                playlist=playlist,
                songs=available_songs,
                existing_song_ids=existing_song_ids,
                search=search,
            )

        added_count = 0

        for song_id in selected_song_ids:
            try:
                song_id_int = int(song_id)
            except ValueError:
                continue

            song = Song.query.filter_by(id=song_id_int, user_id=current_user.id).first()
            if not song:
                continue

            existing_link = PlaylistSong.query.filter_by(
                playlist_id=playlist.id,
                song_id=song.id,
            ).first()

            if existing_link:
                continue

            new_link = PlaylistSong(
                playlist_id=playlist.id,
                song_id=song.id,
            )
            db.session.add(new_link)
            added_count += 1

        db.session.commit()

        if added_count > 0:
            flash(f"{added_count} song(s) added to the playlist successfully.", "success")
        else:
            flash("No new songs were added. Selected songs may already exist in the playlist.", "info")

        return redirect(url_for("playlists.playlist_detail", playlist_id=playlist.id))

    return render_template(
        "playlists/add_songs_to_playlist.html",
        playlist=playlist,
        songs=available_songs,
        existing_song_ids=existing_song_ids,
        search=search,
    )


@playlists_bp.route("/<int:playlist_id>/remove-song/<int:song_id>", methods=["POST"])
@login_required
@active_subscription_required
def remove_song_from_playlist(playlist_id, song_id):
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first_or_404()

    playlist_song = PlaylistSong.query.filter_by(
        playlist_id=playlist.id,
        song_id=song_id,
    ).first_or_404()

    db.session.delete(playlist_song)
    db.session.commit()

    flash("Song removed from playlist successfully.", "success")
    return redirect(url_for("playlists.playlist_detail", playlist_id=playlist.id))