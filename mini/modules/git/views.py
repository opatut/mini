from mini import access
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

@app.route("/repository/<slug>/")
def repository(slug):
    return redirect(url_for("git.browse", slug=slug))

@app.route("/repository/<slug>/history/")
def history(slug):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check("git.repository.%s.history" % repository.slug)
    return render_template("history.html", repository=repository)

@app.route("/repository/<slug>/browse/")
def browse(slug):
    return render_template("repositories.html", repositories=Repository.query.all())
