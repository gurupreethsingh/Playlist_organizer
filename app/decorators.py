# custom decorators will be added in the next step
from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def superadmin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please login to continue.", "warning")
            return redirect(url_for("auth.login"))

        if current_user.role != "superadmin":
            flash("You are not authorized to access that page.", "danger")
            return redirect(url_for("main.home"))

        return view_func(*args, **kwargs)

    return wrapped_view


def subscribed_user_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please login to continue.", "warning")
            return redirect(url_for("auth.login"))

        if current_user.role != "user":
            flash("This page is only available for normal users.", "danger")
            return redirect(url_for("main.home"))

        return view_func(*args, **kwargs)

    return wrapped_view


def active_subscription_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please login to continue.", "warning")
            return redirect(url_for("auth.login"))

        if current_user.role == "superadmin":
            return view_func(*args, **kwargs)

        if not current_user.is_subscription_active:
            flash("Your subscription is inactive. Please contact the administrator.", "warning")
            return redirect(url_for("user.subscription_status"))

        return view_func(*args, **kwargs)

    return wrapped_view