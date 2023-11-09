from headbook import app, oauth
from headbook.modules.utils import safe_redirect_next
from flask_login import login_user
from headbook.modules.user import User
from flask import url_for
import secrets


@app.route('/auth/callback/gitlab')
def auth_callback():
    token = oauth.gitlab.authorize_access_token()

    userinfo = token["userinfo"]

    user = User.get_user(userinfo["preferred_username"])
    print(userinfo)
    if user:
        print("user exists")
        login_user(user)
    else:

        newuser = User({
            "username": userinfo["preferred_username"],
            "password": userinfo["sub_legacy"] + app.config["SECRET_KEY"] + str(secrets.randbits(32)),
            "picture_url": userinfo["picture"],
            "name": userinfo["name"],
            "email": userinfo["email"],
        })

        newuser.save()
        newuser.add_token("gitlab")
        login_user(newuser)

    return safe_redirect_next()


@app.route('/login/gitlab/')
def login_gitlab():
    print(url_for('auth_callback', _external=True))
    return oauth.gitlab.authorize_redirect(url_for('auth_callback', _external=True))
