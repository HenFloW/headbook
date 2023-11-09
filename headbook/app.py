import flask_login
import os
import secrets
from http import HTTPStatus
from flask import (
    Flask,
    abort,
    g,
)
from werkzeug.datastructures import WWWAuthenticate
from base64 import b64decode
from authlib.integrations.flask_client import OAuth
from headbook.modules.db import sql_init
from headbook.modules.utils import debug
from headbook.modules.user import User

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
# For database access


@app.teardown_appcontext
def teardown_db(exception):
    cursor = g.pop("cursor", None)
    if cursor is not None:
        cursor.close()


with app.app_context():
    sql_init()

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

# Routes are moved into __init__.py

################################


@app.before_request
def before_request():
    # can be used to allow particular inline scripts with Content-Security-Policy
    g.csp_nonce = secrets.token_urlsafe(32)

# Can be used to set HTTP headers on the responses


@app.after_request
def after_request(response):
    response.headers["Content-Security-Policy"] = f"script-src 'self' 'nonce-{g.csp_nonce}';"
    return response
