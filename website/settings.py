import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WEBSITE_UPLOAD_PATH= os.path.join(basedir, 'uploads')
    AVATARS_SAVE_PATH= os.path.join(WEBSITE_UPLOAD_PATH, 'avatars')
    AVATARS_SIZE_TUPLE=(30, 100, 200)

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data.db')
    SECRET_KEY = os.getenv("SECRET_KEY", "d3cf9d214a0b4124815f74dffb8758c2")

config = {
    'production': ProductionConfig
}


class Operations:
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'
    CHANGE_EMAIL = 'change-email'


