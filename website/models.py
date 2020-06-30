from website.extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

"""
roles_permissions = db.Table('roles_permissions',
                            db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                             db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
                             )

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    roles = db.relationship('Role', secondary=roles_permissions, back_populates='permissions')

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    users = db.relationship('User', back_populates='role')
    permissions = db.relationship('Permission', secondary=roles_permissions, back_populates='roles')
"""

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(30))
    password_hash = db.Column(db.String(128))
    about = db.Column(db.Text)
    joinDate = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    confirmed = db.Column(db.Boolean, default=False)

    #role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    #role = db.relationship('Role', back_populates='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


"""
#sent by server to the user's email
class EmailSentByServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    email_id = db.Column(db.Integer, db.ForeignKey('email_registered.id'))
    email = db.relationship('EmailRegistered', back_populates='emails_received')

class EmailRegistered(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_addr = db.Column(db.String(50), unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    emails_received = db.relationship('EmailSentByServer', back_populates='email')

"""


