from flask import Flask
from datetime import *
# from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.markdown import Markdown
from os.path import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/mini-test.db'
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = 'CHANGE_ME'

# app.config["ROOTDIR"] = join(dirname(abspath(__file__)), "..")

# app.config.from_pyfile('../config.py', silent = False)

# if not isabs(app.config["REPOHOME"]):
    # app.config["REPOHOME"] = abspath(join(app.config["ROOTDIR"], app.config["REPOHOME"]))

db = SQLAlchemy(app)

Markdown(app, safe_mode="escape")

from mini.core import *

from mini.modules.wiki import ext as wiki
app.register_blueprint(wiki.blueprint, url_prefix='/wiki')

menu = [
    Menu("index", "Index", lambda: url_for("index"), "")
] + wiki.menu

def build_menu(path=""):
    r = []
    for item in menu:
        if item.path == path:
            item.children = build_menu(("%s.%s" % (path, item.name)) if path else item.name)
            r.append(item)
    return r

@app.context_processor
def inject_menu():
    return dict(menu=build_menu())
