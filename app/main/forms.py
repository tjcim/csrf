from flask import request
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError, Length
from wtforms import StringField, SubmitField, TextAreaField, HiddenField

from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)
    ])
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class FavoriteActorForm(FlaskForm):
    token = StringField("Token")
    actor_name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class FavoriteMovieForm(FlaskForm):
    token = HiddenField("Token")
    movie_title = StringField("Title", validators=[DataRequired()])
    submit = SubmitField("Submit")
