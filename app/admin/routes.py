from sqlalchemy import func
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.decorators import superadmin_required
from app.extensions import db
from app.models import Playlist, Song, SubscriptionLog, User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@superadmin_required
def dashboard():
    total_users = User.query.filter_by(role="user").count()
    active_subscriptions = User.query.filter_by(role="user", is_subscription_active=True).count()
    inactive_subscriptions = User.query.filter_by(role="user", is_subscription_active=False).count()

    total_playlists = Playlist.query.count()
    total_songs = Song.query.count()

    total_languages = (
        db.session.query(func.count(func.distinct(Song.language)))
        .filter(Song.language.isnot(None), Song.language != "")
        .scalar()
        or 0
    )

    total_genres = (
        db.session.query(func.count(func.distinct(Song.genre)))
        .filter(Song.genre.isnot(None), Song.genre != "")
        .scalar()
        or 0
    )

    latest_users = (
        User.query.filter_by(role="user")
        .order_by(User.created_at.desc())
        .limit(6)
        .all()
    )

    latest_playlists = Playlist.query.order_by(Playlist.created_at.desc()).limit(6).all()
    latest_songs = Song.query.order_by(Song.uploaded_at.desc()).limit(6).all()
    latest_subscription_logs = SubscriptionLog.query.order_by(SubscriptionLog.created_at.desc()).limit(6).all()

    top_languages = (
        db.session.query(Song.language, func.count(Song.id))
        .filter(Song.language.isnot(None), Song.language != "")
        .group_by(Song.language)
        .order_by(func.count(Song.id).desc())
        .limit(6)
        .all()
    )

    top_genres = (
        db.session.query(Song.genre, func.count(Song.id))
        .filter(Song.genre.isnot(None), Song.genre != "")
        .group_by(Song.genre)
        .order_by(func.count(Song.id).desc())
        .limit(6)
        .all()
    )

    top_artists = (
        db.session.query(Song.artist_name, func.count(Song.id))
        .filter(Song.artist_name.isnot(None), Song.artist_name != "")
        .group_by(Song.artist_name)
        .order_by(func.count(Song.id).desc())
        .limit(6)
        .all()
    )

    users_with_playlist_counts = (
        db.session.query(User, func.count(Playlist.id).label("playlist_count"))
        .outerjoin(Playlist, Playlist.user_id == User.id)
        .filter(User.role == "user")
        .group_by(User.id)
        .order_by(func.count(Playlist.id).desc())
        .limit(6)
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        active_subscriptions=active_subscriptions,
        inactive_subscriptions=inactive_subscriptions,
        total_playlists=total_playlists,
        total_songs=total_songs,
        total_languages=total_languages,
        total_genres=total_genres,
        latest_users=latest_users,
        latest_playlists=latest_playlists,
        latest_songs=latest_songs,
        latest_subscription_logs=latest_subscription_logs,
        top_languages=top_languages,
        top_genres=top_genres,
        top_artists=top_artists,
        users_with_playlist_counts=users_with_playlist_counts,
    )


@admin_bp.route("/users")
@login_required
@superadmin_required
def users():
    search = request.args.get("search", "").strip()

    query = User.query.filter(User.role == "user")

    if search:
        query = query.filter(
            db.or_(
                User.full_name.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
            )
        )

    users = query.order_by(User.created_at.desc()).all()

    user_song_counts = dict(
        db.session.query(Song.user_id, func.count(Song.id))
        .group_by(Song.user_id)
        .all()
    )

    user_playlist_counts = dict(
        db.session.query(Playlist.user_id, func.count(Playlist.id))
        .group_by(Playlist.user_id)
        .all()
    )

    return render_template(
        "admin/users.html",
        users=users,
        search=search,
        user_song_counts=user_song_counts,
        user_playlist_counts=user_playlist_counts,
    )


@admin_bp.route("/users/<int:user_id>/deactivate", methods=["POST"])
@login_required
@superadmin_required
def deactivate_subscription(user_id):
    user = User.query.filter_by(id=user_id, role="user").first_or_404()

    user.is_subscription_active = False

    log = SubscriptionLog(
        user_id=user.id,
        action_type="deactivated",
        action_by=current_user.id,
        remarks="Subscription deactivated by superadmin.",
    )

    db.session.add(log)
    db.session.commit()

    flash(f"Subscription deactivated for {user.full_name}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/reactivate", methods=["POST"])
@login_required
@superadmin_required
def reactivate_subscription(user_id):
    user = User.query.filter_by(id=user_id, role="user").first_or_404()

    user.is_subscription_active = True

    log = SubscriptionLog(
        user_id=user.id,
        action_type="reactivated",
        action_by=current_user.id,
        remarks="Subscription reactivated by superadmin.",
    )

    db.session.add(log)
    db.session.commit()

    flash(f"Subscription reactivated for {user.full_name}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/all-songs")
@login_required
@superadmin_required
def all_songs():
    search = request.args.get("search", "").strip()

    query = Song.query.join(User, User.id == Song.user_id)

    if search:
        query = query.filter(
            db.or_(
                Song.title.ilike(f"%{search}%"),
                Song.artist_name.ilike(f"%{search}%"),
                Song.album_name.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
            )
        )

    songs = query.order_by(Song.uploaded_at.desc()).all()

    return render_template(
        "admin/all_songs.html",
        songs=songs,
        search=search,
    )


@admin_bp.route("/all-playlists")
@login_required
@superadmin_required
def all_playlists():
    search = request.args.get("search", "").strip()

    query = Playlist.query.join(User, User.id == Playlist.user_id)

    if search:
        query = query.filter(
            db.or_(
                Playlist.playlist_name.ilike(f"%{search}%"),
                Playlist.description.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
            )
        )

    playlists = query.order_by(Playlist.created_at.desc()).all()

    playlist_song_counts = dict(
        db.session.query(PlaylistSong.playlist_id, func.count(PlaylistSong.id))
        .group_by(PlaylistSong.playlist_id)
        .all()
    ) if playlists else {}

    return render_template(
        "admin/all_playlists.html",
        playlists=playlists,
        search=search,
        playlist_song_counts=playlist_song_counts,
    )


@admin_bp.route("/subscription-logs")
@login_required
@superadmin_required
def subscription_logs():
    logs = SubscriptionLog.query.order_by(SubscriptionLog.created_at.desc()).all()
    return render_template("admin/subscription_logs.html", logs=logs)