from mini import access, app, menu
from mini.models import Repository, PublicKey
from flask import redirect, url_for, render_template
import git # for type checks

@app.route("/repositories")
@menu.add_view("repositories", "Repositories", "index")
def repositories():
    return render_template("git/repositories.html", repositories=Repository.query.all())

@app.route("/<slug>/")
def repository(slug):
    return redirect(url_for("browse", slug=slug))

@app.route("/<slug>/history/")
def history(slug):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("read"))
    return render_template("git/history.html", repository=repository)

@app.route("/<slug>/browse/")
@app.route("/<slug>/browse/<rev>/")
@app.route("/<slug>/browse/<rev>/<path:path>")
def browse(slug, rev="", path=""):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("read"))

    if not rev:
        rev = repository.git.heads[0].name
    path = path.rstrip("/")

    commit = repository.get_commit(rev)
    if not commit:
        flash("Invalid revision: %s." % rev, "error")
        return redirect(url_for("repository", slug=repository.slug))

    target = commit.tree
    if path:
        target = target / path

    if isinstance(target, git.Blob):
        return render_template("git/file.html", repository=repository, file=target, commit=commit, rev=rev, path=path)
    elif isinstance(target, git.Tree):
        return render_template("git/browse.html", repository=repository, tree=target, commit=commit, rev=rev, path=path)
    else:
        raise Exception("Should reaaally never happen.")

@app.route("/<slug>/history/<rev>/")
def commit(slug, rev):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("read"))

    commit = repository.get_commit(rev)
    return render_template("commit.html", repository=repository, commit=commit, rev=rev)

@app.route("/<slug>/raw/<rev>/<path:path>")
def file_content(slug, rev, path):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("read"))

    commit = repository.get_commit(rev)
    if not commit: abort(404)

    blob = commit.tree / path
    response = main_app.make_response(blob.data_stream.read())
    response.mimetype = blob.mime_type
    return response

@app.route("/<slug>/wiki")
def wiki(slug):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("read"))
    return render_template("wiki.html", repository=repository)

@app.route("/<slug>/admin")
def admin(slug):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("admin"))
    return render_template("admin.html", repository=repository)

