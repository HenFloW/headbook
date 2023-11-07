from flask import render_template, request, session, flash
from flask_login import login_user
from headbook import app
from headbook.modules.utils import debug, safe_redirect_next
from headbook.forms.signup_form import SignupForm
from headbook.modules.user import User
from headbook.modules.utils import debug, safe_redirect_next
from headbook.modules.rate_limiter import rate_limiter


@app.route("/signup/", methods=["GET", "POST"])
def signup():
    """Render (GET) or process (POST) signup form"""

    debug('/signup/ – session:', session, request.host_url)
    form = SignupForm()

    if not form.next.data:
        form.next.data = request.args.get("next")

    if form.is_submitted():
        debug(
            f'Received form:\n    {form.data}\n{"INVALID" if not form.validate() else "valid"} {form.errors}'
        )
        if form.validate():
            username = form.username.data
            password = form.password.data
            user = User.get_user(username)
            if user:
                flash(f"User {username} already exists.")
            else:
                create_user(username, password)
                return safe_redirect_next()
    return render_template("signup.html", form=form)


@rate_limiter(3, "5m")
def create_user(username, password):
    user = User({"username": username, "password": password})
    user.save()
    login_user(user)
    flash(f"User {username} created successfully.")
    return user
