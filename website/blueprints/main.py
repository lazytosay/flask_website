from flask import flash, redirect, Blueprint, render_template, request, abort
from website.extensions import limiter

main_bp = Blueprint('main', __name__)
ip_ban = []
@main_bp.before_request
def block_method():
    """
    comingIp = request.remote_addr
    if comingIp in ip_ban:
        print("the coming ip: ", comingIp)
        abort(403)
    else:
        ip_ban.append(comingIp)
    """
    pass


@main_bp.route('/')
@limiter.limit("2 per second")
def index():
    return render_template('index.html')

@main_bp.route('/about')
@limiter.limit("2 per second")
def about():
    return render_template('about.html')
