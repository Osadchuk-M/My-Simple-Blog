from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, \
    SubmitField
from wtforms.validators import Required, Length, Email, Regexp


class EditProfileForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    name = StringField('Name', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                             'Usernames must have only letters, '
                                                                             'numbers, dots or underscores')])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = PageDownField('About me')
    submit = SubmitField('Save it.')

    def fill_the_form(self, user):
        self.email.data = user.email or ''
        self.name.data = user.name or ''
        self.location.data = user.location or ''
        self.about_me = user.about_me_md or ''


class PostForm(FlaskForm):
    title = StringField('Title', validators=[Required(), Length(1, 64)])
    body = PageDownField('Your post', validators=[Required()])
    submit = SubmitField('Save the post.')

    def fill_the_form(self, post):
        self.title.data = post.title
        self.body.data = post.body

    def clear_fields(self):
        self.title.data, self.body.data = '', ''

