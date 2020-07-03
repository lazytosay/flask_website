from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, Email
from flask_ckeditor import CKEditorField

class QuestionForm(FlaskForm):
    question = CKEditorField('question', validators=[DataRequired(), Length(5,20000)])
    submit = SubmitField('submit')

class AnswerForm(FlaskForm):
    answer = CKEditorField('answer', validators=[DataRequired(), Length(1, 20000)])
    submit = SubmitField('submit')

class CommentForm(FlaskForm):
    comment = TextAreaField('comment', validators=[DataRequired(), Length(1, 1000)])
    submit = SubmitField('submit')