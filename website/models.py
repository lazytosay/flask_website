from website.extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    users = db.relationship('UserCommon', back_populates='role')

    permissions = db.relationship('Permission', secondary='role_permission', back_populates='roles')

    @staticmethod
    def init_role():
        roles_permissions_map = {
            'Locked': ['VISIT'],
            'User': ['VISIT', 'ASK', 'ANSWER', 'REPLY'],
            'Moderator': ['VISIT', 'ASK', 'ANSWER', 'REPLY', 'MODERATE'],
            'Administrator': ['VISIT', 'ASK', 'ANSWER', 'REPLY', 'MODERATE', 'ADMINISTER']
        }

        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.session.add(role)
            role.permission = []
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                #important
                role.permissions.append(permission)
        db.session.commit()

role_permission = db.Table('role_permission',
                           db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                           db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
                           )

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    roles = db.relationship('Role', secondary='role_permission', back_populates='permissions')

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    author_id = db.Column(db.Integer, db.ForeignKey('user_common.id'))
    author = db.relationship('UserCommon', back_populates='comments')

    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])

    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')

class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    question = db.relationship('Question', back_populates='answers')

    author_id = db.Column(db.Integer, db.ForeignKey('user_common.id'))
    author = db.relationship('UserCommon', back_populates='answers')

    replied_id = db.Column(db.Integer, db.ForeignKey('answer.id'))
    replied = db.relationship('Answer', back_populates='replies', remote_side=[id])

    replies = db.relationship('Answer', back_populates='replied', cascade='all, delete-orphan')



class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship('Question', secondary='tags_questions', back_populates='tags')

    #FIXME: may add this later
    #created_by_id = db.Column(db.Integer, db.ForeignKey('Admin.id'))
    #created_by = db.relationship('Admin', back_populates='tags')

    def delete(self):
        default_tag = Tag.query.get(1)
        questions = self.questions[:]

        for q in questions:
            q.tags.remove(self)
            if len(q.tags == 0):
                q.tags.append(default_tag)

        db.session.delete(self)
        db.session.commit()


tags_questions = db.Table('tags_questions',
                          db.Column('tag_id', db.ForeignKey('tag.id')),
                          db.Column('question_id', db.ForeignKey('question.id'))
                          )

class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    collectors = db.relationship('UserCommon', secondary='collections_questions', back_populates='collections')

    author_id = db.Column(db.Integer, db.ForeignKey('user_common.id'))
    author = db.relationship('UserCommon', back_populates='questions')

    answers = db.relationship('Answer', back_populates='question', cascade='all, delete-orphan')

    tags = db.relationship('Tag', secondary='tags_questions', back_populates='questions')



collections_questions = db.Table('collections_questions',
                                 db.Column('collector_id', db.Integer, db.ForeignKey('user_common.id')),
                                db.Column('question_id', db.Integer, db.ForeignKey('question.id')),
                                 db.Column('timestamp', db.DateTime, default=datetime.utcnow)
                                 )


class UserCommon(db.Model, UserMixin):
    #__abstract__=True
    __tablename__ = "user_common"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(128))
    about = db.Column(db.Text)
    joinDate = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_confirmed = db.Column(db.Boolean, default=False)

    collections = db.relationship('Question', secondary='collections_questions', back_populates='collectors')
    questions = db.relationship('Question', back_populates='author', cascade='all, delete-orphan')
    answers = db.relationship('Answer', back_populates='author')
    comments = db.relationship('Comment', back_populates='author')

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', back_populates='users')

    def __init__(self, **kwargs):
        super(UserCommon, self).__init__(**kwargs)
        self.set_role()

    def set_role(self):
        if self.role is None:
            self.role = Role.query.filter_by(name='User').first()
            db.session.commit()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permission_name):
        all = Permission.query.all()
        print("-----all: ", all)
        permission = Permission.query.filter_by(name=permission_name).first()
        return permission is not None and self.role is not None and permission in self.role.permissions

#don't know how to do inheritance with UserMixin yet... will cause errors
#"Columns with foreign keys to other columns "
#sqlalchemy.exc.InvalidRequestError: Columns with foreign keys to other columns must be declared as @declared_attr callables on declarative mixin classes.
"""
class Admin(UserCommon):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)

    tags = db.relationship('Tag', back_populates='created_by')
"""

"""
class RegularUser(UserCommon):
    __tablename__ = 'regular_user'
    id = db.Column(db.Integer, primary_key=True)
"""


