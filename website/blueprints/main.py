from flask import flash, redirect, Blueprint, render_template, request, abort
from website.extensions import limiter

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@limiter.limit("2 per second")
def index():
    return render_template('index.html')


@main_bp.route('/about')
@limiter.limit("2 per minute")
#@limiter.limit("2 per second" , key_func=lambda: current_user.username)
def about():
    return render_template('about.html')
