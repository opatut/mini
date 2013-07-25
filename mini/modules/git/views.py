from mini.modules.git import app, ext
from mini.modules.git.models import Repository, PublicKey
from flask import redirect, url_for, render_template

@app.route("/")
@ext.menu.add_view("git", "Git")
def index():
    return redirect(url_for("git.repositories"))

@app.route("/repositories")
@ext.menu.add_view("repositories", "Repositories", "git")
def repositories():
    return render_template("repositories.html", repositories=Repository.query.all())
