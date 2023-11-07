from flask import jsonify
from flask_login import current_user, login_required
from headbook import app


@app.get("/current_user_id")
@login_required
def get_current_user_id():
    return jsonify(current_user.id)
