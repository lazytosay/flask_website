from flask import Blueprint, url_for, render_template, flash

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/')
def index():
    return "this is chat page..."