from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, URLField, validators


class ProfileForm(FlaskForm):
    username = StringField('Username', render_kw={'readonly': True})
    password = PasswordField('Password', [
        validators.optional(),
        validators.equal_to('password_again', message='match'),
        validators.Length(
            min=8, max=-1, message='be minimum 8 characters long'),
        validators.Regexp(
            '^(?=.*[a-z]).+$', message='contain at least one lowercase letter'),
        validators.Regexp(
            '^(?=.*[A-Z]).+$', message='contain at least one uppercase letter'),
        validators.Regexp(
            '^(?=.*\d).+$', message='contain at least one digit'),
        validators.Regexp('^(?=.*(_|[^\w])).+$', message='contain at least one special character')])
    password_again = PasswordField('Repeat Password')
    birthdate = DateField('Birth date', [validators.optional()])
    color = StringField('Favourite color')
    picture_url = URLField(
        'Picture URL', [validators.url(), validators.optional()])
    about = TextAreaField(
        'About', [validators.optional(), validators.Length(max=600, message='be maximum 600 characters long')])
    save = SubmitField('Save changes')
