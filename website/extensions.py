from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, AnonymousUserMixin
from flask_ckeditor import CKEditor
from flask_moment import Moment
from flask_avatars import Avatars
from flask_wtf import CSRFProtect
from flask_socketio import SocketIO
from sendgrid import SendGridAPIClient
import os

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    from website.models import UserCommon as User
    user = User.query.get_or_404(int(user_id))
    return user

login_manager.login_view = 'auth.login'

ckeditor = CKEditor()

moment = Moment()

avatars = Avatars()

csrf = CSRFProtect()

socket = SocketIO()

sendgrid_client = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))

limiter = Limiter(key_func=get_remote_address, default_limits=["500 per day", "120 per hour"])

class Guest(AnonymousUserMixin):
    def can(self, permission_name):
        return False

    @property
    def is_confirmed(self):
        return False

login_manager .anonymous_user = Guest