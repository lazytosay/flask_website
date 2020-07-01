from website.extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('user_common.id'))
    author = db.relationship('UserCommon', back_populates='comments')

    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])

    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete')

class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    question = db.relationship('Question', back_populates='answers')

    author_id = db.Column(db.Integer, db.ForeignKey('user_common.id'))
    author = db.relationship('UserCommon', back_populates='answers')



class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship('Question', secondary='tags_questions', back_populates='tags')

    #FIXME: may add this later
    #created_by_id = db.Column(db.Integer, db.ForeignKey('Admin.id'))
    #created_by = db.relationship('Admin', back_populates='tags')

tags_questions = db.Table('tags_questions',
                          db.Column('tag_id', db.ForeignKey('tag.id')),
                          db.Column('question_id', db.ForeignKey('question.id'))
                          )

class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    collectors = db.relationship('UserCommon', secondary='collections_questions', back_populates='collectors')

    author_id = db.Column(db.Integer, db.ForeignKey('user_common.id'))
    author = db.relationship('UserCommon', back_populates='questions')

    answers = db.relationship('Answer', back_populates='question')

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
    questions = db.relationship('Question', back_populates='author')
    answers = db.relationship('Answer', back_populates='author')
    comments = db.relationship('Comment', back_populates='author')

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', back_populates='users')


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


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


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    users = db.relationship('UserCommon', back_populates='role')

    permission = db.relationship('Permission', secondary='role_permission', back_populates='roles')

role_permission = db.Table('role_permission',
                           db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                           db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
                           )

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    roles = db.relationship('Role', secondary='role_permission', back_populates='permission')