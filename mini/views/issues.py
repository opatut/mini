from mini import app, menu, access
from mini.models import Issue, Repository
from flask import redirect, url_for, render_template

@app.route("/<slug>/issues/")
def issues(slug):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("read"))
    return render_template("issues/list.html", issues=repository.issues, repository=repository)

@app.route("/<slug>/issues/<number>")
def issue(slug, number):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("read"))
    issue = Issue.query.filter_by(repository_id=repository.id, number=number).first_or_404()
    return render_template("issues/issue.html", issue=issue, repository=repository)
