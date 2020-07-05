from flask import render_template, redirect, flash, url_for
from flask.blueprints import Blueprint
from flask_login import login_user, login_required, current_user, logout_user
from website.extensions import limiter, db
from website.forms.auth import RegisterForm, LoginForm, ForgetPasswordForm, ResetPasswordForm
from website.utils import generate_token, validate_token, check_expiry
from website.sendGrid import send_confirm_email, send_reset_password_email
from website.models import UserCommon as User
from website.settings import Operations

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    if current_user.is_authenticated:
        flash("please logout before resetting your password...")
        return redirect(url_for('main.index'))

    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = generate_token(username=user.username, operation=Operations.RESET_PASSWORD)
            send_reset_password_email(token=token, username=user.username)
            flash("sent reset password email...please change your password in 15 minutes")
            return redirect(url_for('auth.login'))
        flash("invalid email...")
        return redirect(url_for('auth.forget_password'))

    return render_template('auth/forget_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@limiter.limit("3 per day")
def reset_password(token):
    if current_user.is_authenticated:
        flash("please logout before resetting your password...")
        return redirect(url_for('main.index'))

    #check to see if token is expired, we dont have username yet, so we need to use another function
    time_valid = check_expiry(token)
    if not time_valid:
        flash("either the token is expired or its content has been altered, please resend the email...")
        return redirect(url_for('main.index'))

    flash("NOTE: submission will not be accepted if the token is expired, check the email your received or resend the email if submission is rejected")
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None:
            flash('invalid email address, please try again...')
            return redirect(url_for('main.index'))
        if validate_token(username=user.username, token=token, operation=Operations.RESET_PASSWORD):
            user.set_password(form.password.data)
            db.session.commit()
            flash("password updated...")
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid or expired link...')
            return redirect(url_for('auth.forget_password'))

    return render_template('auth/reset_password.html', form=form)



@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit('10/minute')
@limiter.limit('20/day')
def register():
    form = RegisterForm()

    if form.validate_on_submit():

        email = form.email.data.lower()
        name = form.name.data
        username = form.username.data
        password = form.password.data

        user = User(username=username, name=name, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        token = generate_token(username, "confirm")
        send_confirm_email(token=token, username=username)
        flash("Register success!")
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/resend-confirm-email')
@login_required
@limiter.limit("3 per minute")
def resend_confirm_email():
    if current_user.is_confirmed:
        flash("already confirmed your email...")
        return redirect(url_for('main.index'))

    token = generate_token(current_user.username, "confirm")
    send_confirm_email(token=token, username=current_user.username)
    flash("your confirm email will be delivered within 24 hours...")
    return redirect(url_for('main.index'))


@auth_bp.route('/check/<token>')
@login_required
@limiter.limit("3 per hour")
def check(token):
    if current_user.is_confirmed:
        flash("already confirmed....")

    elif validate_token(current_user.username, token, "confirm"):
        flash("email confirmed")
        return redirect(url_for('main.index'))

    else:
        flash("email token not valid...")

    return redirect(url_for('main.index'))

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('10/minute, 100/day')
def login():
    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter(User.email == form.email.data.lower()).first()

        if not user:
            flash("check you account or password...")
            return redirect(url_for('auth.login'))

        password = form.password.data

        if user.validate_password(password):
            login_user(user)
            flash("logged in...")
            return redirect(url_for('main.index'))
        flash("check your account or password...")

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("logged out...")
    return redirect(url_for('main.index'))