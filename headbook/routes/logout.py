from flask import redirect, session
from headbook import app
from flask_login import logout_user


@app.get('/logout/')
def logout_gitlab():
    print('logout', session, session.get('access_token'))
    logout_user()
    return redirect('/')
