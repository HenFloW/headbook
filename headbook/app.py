from flask_login import current_user, login_required, login_user
import flask_login
import flask
import os
import secrets
import json
from datetime import date
from http import HTTPStatus
from flask import (
    Flask,
    abort,
    g,
    jsonify,
    redirect,
    request,
    send_from_directory,
    render_template,
    session,
    url_for,
)
from urllib.parse import urlparse
from werkzeug.datastructures import WWWAuthenticate
from base64 import b64decode
from .login_form import LoginForm
from .profile_form import ProfileForm
from .signup_form import SignupForm
from .modules.hashing import check_password, hash_password
from authlib.integrations.flask_client import OAuth
from .modules.db import sql_execute, sql_init
from .modules.utils import debug, prefers_json
from .modules.user import User

################################
# Set up app
APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(APP_PATH, "templates/"),
    static_folder=os.path.join(APP_PATH, "static/"),
)

# You can also load app configuration from a Python file – this could
# be a convenient way of loading secret tokens and other configuration data
# that shouldn't be pushed to Git.
#    app.config.from_pyfile(os.path.join(APP_PATH, 'secrets'))

# The secret key enables storing encrypted session data in a cookie (TODO: make a secure random key for this! and don't store it in Git!)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
app.config["TEMPLATES_AUTO_RELOAD"] = True
# app.config["GITLAB_BASE_URL"] = 'https://git.app.uib.no/'
# app.config["GITLAB_CLIENT_ID"] = ''
# app.config["GITLAB_CLIENT_SECRET"] = ''
# Pick appropriate values for these

app.config['SESSION_COOKIE_NAME'] = "headbook-session"
app.config['SESSION_COOKIE_SAMESITE'] = "Lax"
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Add a login manager to the app

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

oauth = OAuth(app)
oauth.register(
    name="gitlab",
    client_id=os.getenv("GITLAB_CLIENT_ID"),
    client_secret=os.getenv("GITLAB_CLIENT_SECRET"),
    server_metadata_url='https://git.app.uib.no/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email api read_api'},
)

################################


################################
# Class to store user info
# UserMixin provides us with an `id` field and the necessary methods (`is_authenticated`, `is_active`, `is_anonymous` and `get_id()`).
# Box makes it behave like a dict, but also allows accessing data with `user.key`.


# This method is called whenever the login manager needs to get
# the User object for a given user id – for example, when it finds
# the id of a logged in user in the session data (session['_user_id'])
@login_manager.user_loader
def user_loader(user_id):
    return User.get_user(user_id)

# This method is called to get a User object based on a request,
# for example, if using an api key or authentication token rather
# than getting the user name the standard way (from the session cookie)


@login_manager.request_loader
def request_loader(request):
    # Even though this HTTP header is primarily used for *authentication*
    # rather than *authorization*, it's still called "Authorization".
    auth = request.headers.get("Authorization")

    # If there is not Authorization header, do nothing, and the login
    # manager will deal with it (i.e., by redirecting to a login page)
    if not auth:
        return

    (auth_scheme, auth_params) = auth.split(maxsplit=1)
    auth_scheme = auth_scheme.casefold()
    if auth_scheme == "basic":  # Basic auth has username:password in base64
        # TODO: it's probably a bad idea to implement Basic authentication anyway
        (uname, passwd) = (
            b64decode(auth_params.encode(errors="ignore"))
            .decode(errors="ignore")
            .split(":", maxsplit=1)
        )
        debug(f"Basic auth: {uname}:{passwd}")
        u = User.get_user(uname)
        if u and u.password == passwd:
            return u
    elif auth_scheme == "bearer":  # Bearer auth contains an access token;
        # an 'access token' is a unique string that both identifies
        # and authenticates a user, so no username is provided (unless
        # you encode it in the token – see JWT (JSON Web Token), which
        # encodes credentials and (possibly) authorization info)
        debug(f"Bearer auth: {auth_params}")
        # TODO
    # For other authentication schemes, see
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication

    # If we failed to find a valid Authorized header or valid credentials, fail
    # with "401 Unauthorized" and a list of valid authentication schemes
    # (The presence of the Authorized header probably means we're talking to
    # a program and not a user in a browser, so we should send a proper
    # error message rather than redirect to the login page.)
    # (If an authenticated user doesn't have authorization to view a page,
    # Flask will send a "403 Forbidden" response, so think of
    # "Unauthorized" as "Unauthenticated" and "Forbidden" as "Unauthorized")
    abort(
        HTTPStatus.UNAUTHORIZED,
        www_authenticate=WWWAuthenticate("Basic realm=headbook, Bearer"),
    )

################################
# ROUTES – these get called to handle requests
#
#    Before we get this far, Flask has set up a session store with a session cookie, and Flask-Login
#    has dealt with authentication stuff (for routes marked `@login_required`)
#
#    Request data is available as global context variables:
#      * request – current request object
#      * session – current session (stores arbitrary session data in a dict-like object)
#      * g – can store whatever data you like while processing the current request
#      * current_user – a User object with the currently logged in user (if any)


@app.get("/current_user_id")
@login_required
def get_current_user_id():
    return jsonify(current_user.id)


@app.get("/")
@app.get("/index.html")
@login_required
def index_html():
    """Render the home page"""

    return render_template("home.html")


# by default, path parameters (filename, ext) match any string not including a '/'
@app.get("/<filename>.<ext>")
def serve_static(filename, ext):
    """Serve files from the static/ subdirectory"""

    # browsers can be really picky about file types, so it's important
    # to set this correctly, particularly for JS and CSS
    file_types = {
        "js": "application/javascript",
        "ico": "image/vnd.microsoft.icon",
        "png": "image/png",
        "html": "text/html",
        "css": "text/css",
    }

    if ext in file_types:
        return send_from_directory(
            app.static_folder, f"{filename}.{ext}", mimetype=file_types[ext]
        )
    else:
        abort(404)


@app.route("/login/", methods=["GET", "POST"])
def login():
    """Render (GET) or process (POST) login form"""

    debug('/login/ – session:', session, request.host_url)
    form = LoginForm()

    if not form.next.data:
        # set 'next' field from URL parameters
        form.next.data = flask.request.args.get("next")

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

                flask.flash(f"User {user.username} Logged in successfully.")

                return safe_redirect_next()
    return render_template("login.html", form=form)


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


@app.get('/logout/')
def logout_gitlab():
    print('logout', session, session.get('access_token'))
    flask_login.logout_user()
    return redirect('/')


@app.route("/signup/", methods=["GET", "POST"])
def signup():
    """Render (GET) or process (POST) signup form"""

    debug('/signup/ – session:', session, request.host_url)
    form = SignupForm()

    if not form.next.data:
        form.next.data = flask.request.args.get("next")

    if form.is_submitted():
        debug(
            f'Received form:\n    {form.data}\n{"INVALID" if not form.validate() else "valid"} {form.errors}'
        )
        if form.validate():
            username = form.username.data
            password = form.password.data
            user = User.get_user(username)
            if user:
                flask.flash(f"User {username} already exists.")
            else:
                user = User({"username": username, "password": password})
                user.save()
                login_user(user)
                flask.flash(f"User {username} created successfully.")
                return safe_redirect_next()
    return render_template("signup.html", form=form)


@app.route("/profile/", methods=["GET", "POST", "PUT"])
@login_required
def my_profile():
    """Display or edit user's profile info"""
    debug("/profile/ – current user:", current_user, request.host_url)

    form = ProfileForm()
    if form.is_submitted():
        debug(
            f'Received form:\n    {form.data}\n    {f"INVALID: {form.errors}" if not form.validate() else "ok"}'
        )
        if form.validate():
            if form.password.data:  # change password if user set it
                current_user.password = hash_password(form.password.data)
            if form.birthdate.data:  # change birthday if set
                current_user.birthdate = form.birthdate.data.isoformat()
            # TODO: do we need additional validation for these?
            current_user.color = form.color.data
            current_user.picture_url = form.picture_url.data
            current_user.about = form.about.data
            current_user.save()
        else:
            pass  # The profile.html template will display any errors in form.errors
    else:  # fill in the form with the user's info
        form.username.data = current_user.username
        form.password.data = ""
        form.password_again.data = ""
        # only set this if we have a valid date
        form.birthdate.data = current_user.get("birthdate") and date.fromisoformat(
            current_user.get("birthdate")
        )
        form.color.data = current_user.get("color", "")
        form.picture_url.data = current_user.get("picture_url", "")
        form.about.data = current_user.get("about", "")

    return render_template("profile.html", form=form, user=current_user)


@app.get("/users/")
@login_required
def get_users():
    rows = sql_execute("SELECT id, username FROM users;").fetchall()

    result = []
    for row in rows:
        user = User({"id": row[0], "username": row[1]})
        result.append(user)

    if prefers_json():
        return jsonify(result)
    else:
        return render_template("users.html", users=result)


@app.get("/users/<userid>")
@login_required
def get_user(userid):
    if userid == 'me':
        u = current_user
    else:
        u = User.get_user(userid)

    status = current_user.friend_status(u)

    if status != "friends" and status != "requested" and status != "self":
        u = {
            "id": u.id,
            "username": u.username,
            "friend status": status,
        }
    else:
        u = u.to_dict()
        u["friend status"] = status
        if status == "self":
            u[""] = "Your profile"
            del u["friend status"]

    if u:
        try:
            del u["password"]  # hide the password, just in case
        except KeyError:
            pass
        if prefers_json():
            return jsonify(u)
        else:
            return render_template("users.html", users=[u])
    else:
        abort(404)


@app.get("/buddies/")
@login_required
def get_buddies():
    users = sql_execute(
        "SELECT id, username, info FROM users WHERE id IN (SELECT user1_id FROM buddies WHERE user2_id = ?);", current_user.id
    ).fetchall()

    pending = sql_execute(
        "SELECT id, username, info FROM users WHERE id IN (SELECT user2_id FROM buddies WHERE user1_id = ? AND user2_id NOT IN (SELECT user1_id FROM buddies WHERE user2_id = ?));", current_user.id, current_user.id
    ).fetchall()

    response = []
    users.extend(pending)

    for user in users:
        response.append({"id": user[0], "username": user[1], "friendship": current_user.friend_status(
            User.get_user(user[0])), "info": json.loads(user[2])})

    if prefers_json():
        return jsonify(response)
    else:
        return render_template("buddies.html", users=response)


@app.route("/buddies/<userid>", methods=["POST", "DELETE", "GET"])
@login_required
def get_buddie(userid):
    user = User.get_user(userid)

    if (not user):
        flask.flash(f"User {userid} does not exist.")
        return jsonify({
            "ok": False,
            "error": "Invalid user",
        })

    if (request.method == "GET"):
        status = current_user.friend_status(user)
        return jsonify({
            "ok": True,
            "status": status,
        })

    action = request.headers.get("action")

    if (not action):
        return jsonify({
            "ok": False,
            "error": "No action specified",
        })

    if (current_user.id == user.id):
        flask.flash(f"Cannot add self as buddy.")
        return jsonify({
            "ok": False,
            "error": "Cannot add self as buddy",
        })

    if request.method == "POST":
        current_user.add_buddy(user)
        return jsonify({
            "ok": True,
            "action": action,
            "user": user.id,
        })
    elif request.method == "DELETE":
        current_user.delete_buddy(user)
        return jsonify({
            "ok": True,
            "action": action,
            "user": user.id,
        })

    return jsonify(
        {
            "ok": False,
            "error": "Invalid method",
        }
    )


@app.before_request
def before_request():
    # can be used to allow particular inline scripts with Content-Security-Policy
    g.csp_nonce = secrets.token_urlsafe(32)

# Can be used to set HTTP headers on the responses


@app.after_request
def after_request(response):
    response.headers["Content-Security-Policy"] = f"script-src 'self' 'nonce-{g.csp_nonce}';"
    return response


def get_safe_redirect_url():
    # see discussion at
    # https://stackoverflow.com/questions/60532973/how-do-i-get-a-is-safe-url-function-to-use-with-flask-and-how-does-it-work/61446498#61446498
    next = request.values.get('next')
    if next:
        url = urlparse(next)
        if not url.scheme and not url.netloc:  # ignore if absolute url
            return url.path   # use only the path
    return None


def safe_redirect_next():
    next = get_safe_redirect_url()
    return redirect(next or '/')

# For full RFC2324 compatibilty


@app.get("/coffee/")
def nocoffee():
    abort(418)


@app.route("/coffee/", methods=["POST", "PUT"])
def gotcoffee():
    return "Thanks!"


################################
# For database access

@app.teardown_appcontext
def teardown_db(exception):
    cursor = g.pop("cursor", None)

    if cursor is not None:
        cursor.close()


with app.app_context():
    sql_init()
