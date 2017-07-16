from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, \
    SubmitField
from wtforms.validators import Required, Length, Email, Regexp


class CommentForm(FlaskForm):
    email = StringField('Your email', validators=[Required(), Email()])
    body = TextAreaField('Your comment', validators=[Required()])
    submit = SubmitField('Submit')
