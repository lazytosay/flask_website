from website.extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    name = db.Column(db.String(30))
    email = db.Column(db.String(50))
    password_hash = db.Column(db.String(128))
    about = db.Column(db.Text)
    joinDate = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class Blocked_Temp_IP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_addr = db.Column(db.String(128))
    block_start = db.Column(db.DateTime, default=datetime.utcnow)
    block_end = db.Column(db.DateTime)