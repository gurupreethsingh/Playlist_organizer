from datetime import date

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    DateField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,
    ValidationError,
)

from app.models import User


class RegisterForm(FlaskForm):
    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(message="Full name is required."),
            Length(min=2, max=150, message="Full name must be between 2 and 150 characters."),
        ],
    )

    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username is required."),
            Length(min=3, max=80, message="Username must be between 3 and 80 characters."),
        ],
    )

    email = StringField(
        "Email Address",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address."),
            Length(max=120),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=6, max=128, message="Password must be between 6 and 128 characters."),
        ],
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo("password", message="Passwords do not match."),
        ],
    )

    submit = SubmitField("Create Account")

    def validate_username(self, field):
        existing_user = User.query.filter_by(username=field.data.strip()).first()
        if existing_user:
            raise ValidationError("This username is already taken.")

    def validate_email(self, field):
        existing_user = User.query.filter_by(email=field.data.strip().lower()).first()
        if existing_user:
            raise ValidationError("An account with this email already exists.")


class LoginForm(FlaskForm):
    email = StringField(
        "Email Address",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address."),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
        ],
    )

    remember_me = BooleanField("Remember me")
    submit = SubmitField("Login")


class ForgotPasswordForm(FlaskForm):
    email = StringField(
        "Email Address",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Enter a valid email address."),
        ],
    )

    submit = SubmitField("Send Reset Link")


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=6, max=128, message="Password must be between 6 and 128 characters."),
        ],
    )

    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo("password", message="Passwords do not match."),
        ],
    )

    submit = SubmitField("Reset Password")


class PlaylistForm(FlaskForm):
    playlist_name = StringField(
        "Playlist Name",
        validators=[
            DataRequired(message="Playlist name is required."),
            Length(min=2, max=150),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[Optional(), Length(max=1000)],
    )

    submit = SubmitField("Save Playlist")


class SongUploadForm(FlaskForm):
    title = StringField(
        "Song Title",
        validators=[DataRequired(), Length(min=1, max=200)],
    )

    artist_name = StringField(
        "Artist Name",
        validators=[DataRequired(), Length(min=1, max=150)],
    )

    album_name = StringField(
        "Album Name",
        validators=[Optional(), Length(max=150)],
    )

    language = SelectField(
        "Language",
        choices=[
            ("", "Select Language"),
            ("English", "English"),
            ("Hindi", "Hindi"),
            ("Tamil", "Tamil"),
            ("Telugu", "Telugu"),
            ("Kannada", "Kannada"),
            ("Malayalam", "Malayalam"),
            ("Punjabi", "Punjabi"),
            ("Other", "Other"),
        ],
        validators=[Optional()],
    )

    genre = SelectField(
        "Genre",
        choices=[
            ("", "Select Genre"),
            ("Melody", "Melody"),
            ("Romantic", "Romantic"),
            ("Sad", "Sad"),
            ("Party", "Party"),
            ("Devotional", "Devotional"),
            ("Classical", "Classical"),
            ("Hip Hop", "Hip Hop"),
            ("Pop", "Pop"),
            ("Rock", "Rock"),
            ("Other", "Other"),
        ],
        validators=[Optional()],
    )

    release_date = DateField(
        "Release Date",
        validators=[Optional()],
        format="%Y-%m-%d",
    )

    movie_name = StringField(
        "Movie Name",
        validators=[Optional(), Length(max=150)],
    )

    singer_gender = SelectField(
        "Singer Type",
        choices=[
            ("", "Select Singer Type"),
            ("Male", "Male"),
            ("Female", "Female"),
            ("Duet", "Duet"),
            ("Mixed", "Mixed"),
        ],
        validators=[Optional()],
    )

    duration = StringField(
        "Duration",
        validators=[Optional(), Length(max=20)],
    )

    is_movie_song = BooleanField("Is this a movie song?")
    is_private_album = BooleanField("Is this from a private album?")

    audio_file = FileField(
        "Upload MP3 File",
        validators=[
            DataRequired(message="Please upload an MP3 file."),
            FileAllowed(["mp3"], "Only MP3 files are allowed."),
        ],
    )

    submit = SubmitField("Upload Song")

    def validate_release_date(self, field):
        if field.data and field.data > date.today():
            raise ValidationError("Release date cannot be in the future.")


class SongEditForm(FlaskForm):
    title = StringField(
        "Song Title",
        validators=[DataRequired(), Length(min=1, max=200)],
    )

    artist_name = StringField(
        "Artist Name",
        validators=[DataRequired(), Length(min=1, max=150)],
    )

    album_name = StringField(
        "Album Name",
        validators=[Optional(), Length(max=150)],
    )

    language = SelectField(
        "Language",
        choices=[
            ("", "Select Language"),
            ("English", "English"),
            ("Hindi", "Hindi"),
            ("Tamil", "Tamil"),
            ("Telugu", "Telugu"),
            ("Kannada", "Kannada"),
            ("Malayalam", "Malayalam"),
            ("Punjabi", "Punjabi"),
            ("Other", "Other"),
        ],
        validators=[Optional()],
    )

    genre = SelectField(
        "Genre",
        choices=[
            ("", "Select Genre"),
            ("Melody", "Melody"),
            ("Romantic", "Romantic"),
            ("Sad", "Sad"),
            ("Party", "Party"),
            ("Devotional", "Devotional"),
            ("Classical", "Classical"),
            ("Hip Hop", "Hip Hop"),
            ("Pop", "Pop"),
            ("Rock", "Rock"),
            ("Other", "Other"),
        ],
        validators=[Optional()],
    )

    release_date = DateField(
        "Release Date",
        validators=[Optional()],
        format="%Y-%m-%d",
    )

    movie_name = StringField(
        "Movie Name",
        validators=[Optional(), Length(max=150)],
    )

    singer_gender = SelectField(
        "Singer Type",
        choices=[
            ("", "Select Singer Type"),
            ("Male", "Male"),
            ("Female", "Female"),
            ("Duet", "Duet"),
            ("Mixed", "Mixed"),
        ],
        validators=[Optional()],
    )

    duration = StringField(
        "Duration",
        validators=[Optional(), Length(max=20)],
    )

    is_movie_song = BooleanField("Is this a movie song?")
    is_private_album = BooleanField("Is this from a private album?")

    submit = SubmitField("Update Song")

    def validate_release_date(self, field):
        if field.data and field.data > date.today():
            raise ValidationError("Release date cannot be in the future.")