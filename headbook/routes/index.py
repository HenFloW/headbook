from flask import render_template
from flask_login import login_required
from headbook import app


@app.get("/")
@app.get("/index.html")
@login_required
def index_html():
    """Render the home page"""
    return render_template("home.html")
