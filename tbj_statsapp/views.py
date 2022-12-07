"""Route requests with Flask"""

from flask import current_app as app
from flask import render_template


@app.route("/")
def index():
    """Render home page"""
    return render_template("index.html")


@app.route("/teams")
def teams():
    """Render teams page"""
    return render_template("teams.html")
