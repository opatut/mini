from datetime import *
from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.markdown import Markdown
from mini.base.minicore import MiniCore

app = Flask(__name__)
app.config.from_pyfile('../config/core.config.py', silent=True)
db = SQLAlchemy(app)
Markdown(app, safe_mode="escape")

from mini.base.minicore import MiniCore
core = MiniCore(app)

def build_menu(path=""):
    r = []
    for item in core.menu_items:
        if item.path == path:
            item.children = build_menu(("%s.%s" % (path, item.name)) if path else item.name)
            r.append(item)
    r.sort(key=lambda x: x.index)
    return r

@app.context_processor
def inject_menu():
    return dict(menu=build_menu())

@app.errorhandler(404)
@app.errorhandler(403)
@app.errorhandler(500)
def error(error):
    return render_template("_error.html", error=error)
