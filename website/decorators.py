from functools import wraps

from flask import Markup, flash, url_for, redirect, abort
from flask_login import current_user

def confirm_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_confirmed:
            message = Markup(
                'Please confirm your account first.'
                'Not receive the email?'
                '<a class="alert-link" href="%s">Resend Confirm Email</a>'%
                url_for('auth.resend_confirm_email')
            )
            flash(message)
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return decorated_function


def permission_required(permission_name):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission_name):
                flash("doesn't have permission: " + permission_name)
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator