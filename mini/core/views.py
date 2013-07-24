from mini import app
from flask import render_template, flash, abort

@app.route("/")
def index():
    return render_template("index.html")

@app.errorhandler(404)
@app.errorhandler(403)
@app.errorhandler(500)
def error(error):
    return render_template("_error.html", error=error)
