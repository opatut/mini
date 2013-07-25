from mini.modules.core import app, ext
from flask import render_template, flash, abort

@app.route("/")
@ext.menu.add_view("index", "Index", index=-100)
def index():
    return render_template("index.html")

@app.route("/settings/")
@ext.menu.add_view("settings", "Settings", index=100)
def settings():
    return render_template("settings.html")
