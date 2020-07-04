from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, Email

from website.models import UserCommon

class ResetPasswordForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Length(1, 50), Email()])
    password = PasswordField('password', validators=[EqualTo('password2'), DataRequired(), Length(8, 128)])
    password2 = PasswordField('confirm password', validators=[DataRequired()])
    submit = SubmitField('submit')

class ForgetPasswordForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Length(3, 50), Email()])
    submit = SubmitField('submit')

class RegisterForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(1, 30)])
    email = StringField('email', validators=[DataRequired(), Length(3, 50), Email()])
    username = StringField('username', validators=[DataRequired(), Length(5, 30),
                                                   Regexp('^[a-zA-Z0-9]*$',
                                                          message="The username should contain only a-z A-Z and 0-9")])
    password =PasswordField('password', validators=[
        DataRequired(), Length(8, 128), EqualTo('password2')])

    password2 = PasswordField('confirm password', validators=[DataRequired()])
    submit = SubmitField('submit')

    def validate_email(self, field):
        if UserCommon.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('The email is already in use...')

    def validate_username(self, field):
        if UserCommon.query.filter_by(username=field.data).first():
            raise ValidationError('The username is already in user...')

class LoginForm(FlaskForm):
    email = StringField('email', validators=[Email(), DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), Length(8, 128)])
    remember_me = BooleanField('remember me')
    submit = SubmitField('submit')


