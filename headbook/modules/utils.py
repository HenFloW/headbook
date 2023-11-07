from flask import request, session
import sys


def debug(*args, **kwargs):
    if request and '_user_id' in session:
        print(f"[user={session.get('_user_id')}]  ", end='', file=sys.stderr)
    print(*args, file=sys.stderr, **kwargs)


def prefers_json():
    return request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json'
