from flask import render_template, redirect, flash, url_for
from flask.blueprints import Blueprint
from flask_login import login_user, login_required, current_user, logout_user
from website.extensions import limiter, db
from website.forms.auth import RegisterForm, LoginForm
from website.utils import generate_token, validate_token
from website.sendGrid import send_confirm_email
from website.models import User

auth_bp = Blueprint('auth', __name__)

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
        send_confirm_email(url_for('auth.check', token=token, _external=True), username=username)
        flash("Register success!")
        return redirect(url_for('main.index'))
    return render_template('register.html', form=form)


@auth_bp.route('/check/<token>')
@login_required
@limiter.limit("5 per hour")
def check(token):
    if validate_token(current_user.username, token, "confirm"):
        flash("email confirmed")
        return redirect(url_for('main.index'))

    flash("email token not valid...")
    return redirect(url_for('main.index'))

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('10/minute')
def login():
    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter(User.email == form.email.data.lower()).first()

        if not user:
            flash("account not exists...")
            return redirect(url_for('auth.login'))

        password = form.password.data

        if user.validate_password(password):
            login_user(user)
            flash("logged in...")
            return redirect(url_for('main.index'))

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("logged out...")
    return redirect(url_for('main.index'))