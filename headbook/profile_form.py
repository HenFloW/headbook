from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, URLField, validators


class ProfileForm(FlaskForm):
    username = StringField('Username', render_kw={'readonly': True})
    password = PasswordField('Password', [
        validators.optional(),
        validators.equal_to('password_again', message='Passwords must match'), 
        validators.Length(min=8, max=-1, message='Password must be minimum 8 characters long'), 
        validators.Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*(_|[^\w])).+$', message='Password must contain at least one lowercase letter, one uppercase letter, one digit and one special character')])
    password_again = PasswordField('Repeat Password')
    birthdate = DateField('Birth date', [validators.optional()])
    color = StringField('Favourite color')
    picture_url = URLField('Picture URL', [validators.url(), validators.optional()])
    about = TextAreaField('About')
    save = SubmitField('Save changes')

