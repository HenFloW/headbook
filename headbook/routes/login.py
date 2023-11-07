from flask import render_template, request, session, flash
from flask_login import login_user
from headbook import app, user_loader
from headbook.modules.utils import debug, safe_redirect_next
from headbook.forms.login_form import LoginForm
from headbook.modules.hashing import check_password


@app.route("/login/", methods=["GET", "POST"])
def login():
    """Render (GET) or process (POST) login form"""

    debug('/login/ – session:', session, request.host_url)
    form = LoginForm()

    if not form.next.data:
        # set 'next' field from URL parameters
        form.next.data = request.args.get("next")

    if form.is_submitted():
        debug(
            f'Received form:\n    {form.data}\n{"INVALID" if not form.validate() else "valid"} {form.errors}'
        )
        if form.validate():
            username = form.username.data
            password = form.password.data
            user = user_loader(username)
            if user and check_password(user.password, password):
                # automatically sets logged in session cookie
                login_user(user)

                flash(f"User {user.username} Logged in successfully.")

                return safe_redirect_next()
    return render_template("login.html", form=form)
