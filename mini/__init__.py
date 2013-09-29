from datetime import *
from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.markdown import Markdown
from flask.ext.login import LoginManager, current_user
from flask.ext.sendmail import Mail
from mini.util import AccessControl, AnonymousUser

app = Flask(__name__)
app.config.from_pyfile('../config.py', silent=True)

db = SQLAlchemy(app)

mail = Mail(app)

Markdown(app, safe_mode="escape")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "core.login"
login_manager.login_message = u"Please log in to show this page."
login_manager.login_message_category = "warning"
login_manager.anonymous_user = AnonymousUser

access = AccessControl(current_user)

from mini.filters import *
from mini.forms import *
from mini.models import *
from mini.views import *

@app.errorhandler(404)
@app.errorhandler(403)
@app.errorhandler(500)
@app.errorhandler(501)
def error(error):
    return render_template("_error.html", error=error)
