from headbook import app
from flask import jsonify, render_template, abort
from flask_login import login_required, current_user
from headbook.modules.user import User
from headbook.modules.utils import prefers_json
from headbook.modules.db import sql_execute


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
