from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, validators


class SignupForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3, max=25, message='Username must be between 3 and 25 characters long')])
    password = PasswordField('Password', [validators.equal_to('password_again', message='Passwords must match'), validators.Length(min=8, max=-1, message='Password must be minimum 8 characters long'), validators.Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*(_|[^\w])).+$', message='Password must contain at least one lowercase letter, one uppercase letter, one digit and one special character')])
    password_again = PasswordField('Repeat Password')
    signup = SubmitField('Signup')
    next = HiddenField()

