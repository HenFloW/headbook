from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, validators

class SignupForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3, max=25, message='Username must be between 3 and 25 characters long')])
    password = PasswordField('Password', [
        validators.equal_to('password_again', message='match'),
        validators.Length(min=8, max=-1, message='be minimum 8 characters long'), 
        validators.Regexp('^(?=.*[a-z]).+$', message='contain at least one lowercase letter'),
        validators.Regexp('^(?=.*[A-Z]).+$', message='contain at least one uppercase letter'),
        validators.Regexp('^(?=.*\d).+$', message='contain at least one digit'),
        validators.Regexp('^(?=.*(_|[^\w])).+$', message='contain at least one special character')])
    password_again = PasswordField('Repeat Password')
    signup = SubmitField('Signup')
    next = HiddenField()

