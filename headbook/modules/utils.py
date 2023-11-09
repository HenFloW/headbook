from flask import request, session, redirect
import sys
from urllib.parse import urlparse


def debug(*args, **kwargs):
    if request and '_user_id' in session:
        print(f"[user={session.get('_user_id')}]  ", end='', file=sys.stderr)
    print(*args, file=sys.stderr, **kwargs)


def prefers_json():
    return request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json'


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
