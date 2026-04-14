import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure required folders exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    # Import models so Flask-Migrate can detect them
    from app import models

    # Register blueprints
    from app.main.routes import main_bp
    app.register_blueprint(main_bp)

    # These blueprints will be added in next steps
    from app.auth.routes import auth_bp
    from app.user.routes import user_bp
    from app.admin.routes import admin_bp
    from app.songs.routes import songs_bp
    from app.playlists.routes import playlists_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(songs_bp)
    app.register_blueprint(playlists_bp)

    return app