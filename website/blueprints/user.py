from flask import Blueprint, render_template, redirect, url_for, send_from_directory, current_app
from website.models import UserCommon as User

user_bp = Blueprint('user', __name__)

@user_bp.route("/<username>")
def index(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('/user/index.html', user=user)

@user_bp.route("/avatars/<path:filename>")
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)