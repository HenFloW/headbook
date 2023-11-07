from flask import render_template, request, jsonify
from flask_login import login_required, current_user
import flask
from headbook import app
from headbook.modules.utils import prefers_json
from headbook.modules.user import User
from headbook.modules.db import sql_execute
import json


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
