from datetime import *
from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.markdown import Markdown
from flask.ext.login import LoginManager, current_user
from mini.base.minicore import MiniCore
from mini.base.util import AccessControl, AnonymousUser

app = Flask(__name__)
app.config.from_pyfile('../config/core.config.py', silent=True)

db = SQLAlchemy(app)

Markdown(app, safe_mode="escape")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "core.login"
login_manager.login_message = u"Please log in to show this page."
login_manager.login_message_category = "warning"
login_manager.anonymous_user = AnonymousUser

access = AccessControl(current_user)

from mini.base.minicore import MiniCore
core = MiniCore(app)

def build_menu(path=""):
    r = []
    for item in core.menu_items:
        if item.is_shown() and item.path == path:
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
