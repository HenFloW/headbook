from flask import abort
from headbook import app


@app.get("/coffee/")
def nocoffee():
    abort(418)


@app.route("/coffee/", methods=["POST", "PUT"])
def gotcoffee():
    return "Thanks!"
