from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.forms import ForgotPasswordForm, LoginForm, RegisterForm, ResetPasswordForm
from app.models import User
from app.utils import (
    get_valid_password_reset_token,
    mark_password_reset_token_used,
    save_password_reset_token,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        if current_user.role == "superadmin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("user.dashboard"))

    form = RegisterForm()

    if form.validate_on_submit():
        new_user = User(
            full_name=form.full_name.data.strip(),
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            role="user",
            is_subscription_active=True,
            is_active_user=True,
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        flash("Registration successful. Welcome to Playlist Organizer.", "success")
        return redirect(url_for("user.dashboard"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.role == "superadmin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("user.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()

        if not user or not user.check_password(form.password.data):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form=form)

        if not user.is_active_user:
            flash("This account is currently inactive. Please contact the administrator.", "warning")
            return render_template("auth/login.html", form=form)

        login_user(user, remember=form.remember_me.data)

        flash("Login successful.", "success")

        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)

        if user.role == "superadmin":
            return redirect(url_for("admin.dashboard"))

        if not user.is_subscription_active:
            flash("Your subscription is inactive. Some features may be restricted.", "warning")

        return redirect(url_for("user.dashboard"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("main.home"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        if current_user.role == "superadmin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("user.dashboard"))

    form = ForgotPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()

        if user:
            token_record = save_password_reset_token(
                user,
                expiry_minutes=current_app.config.get("RESET_TOKEN_EXPIRY_MINUTES", 30),
            )

            reset_link = url_for("auth.reset_password", token=token_record.token, _external=True)

            print("\n" + "=" * 80)
            print("PASSWORD RESET LINK")
            print(reset_link)
            print("=" * 80 + "\n")

            flash(
                "A password reset link has been generated. For now, check your terminal/console output.",
                "success",
            )
        else:
            flash(
                "If an account with that email exists, a reset link has been generated.",
                "info",
            )

        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html", form=form)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        if current_user.role == "superadmin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("user.dashboard"))

    token_record = get_valid_password_reset_token(token)

    if not token_record:
        flash("This reset link is invalid or has expired.", "danger")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user = token_record.user
        user.set_password(form.password.data)

        db.session.commit()
        mark_password_reset_token_used(token_record)

        flash("Your password has been reset successfully. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form)