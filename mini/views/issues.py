from mini import app, menu, access, db
from mini.models import Issue, Repository, User
from flask import redirect, url_for, render_template, request, flash

@app.route("/<slug>/issues/")
def issues(slug):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("read"))
    return render_template("issues/list.html", issues=repository.issues, repository=repository)

@app.route("/<slug>/issues/<number>", methods=("GET", "POST"))
def issue(slug, number):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("read"))
    issue = Issue.query.filter_by(repository_id=repository.id, number=number).first_or_404()

    if request.method == "POST" and "save-status" in request.args:
        issue.status = request.form.get("status")
        issue.assignee = User.query.filter_by(id=request.form.get("assignee")).first()
        issue.issue_tags = [tag for tag in repository.issue_tags if str(tag.id) in request.form.getlist("tag")]

        if not issue.status in ("open", "discussion", "wip", "invalid", "closed"):
            flash("Please select a valid issue state.", "error")
        elif not issue.assignee or not issue.assignee.has_permission(repository.get_permission("read")):
            flash("Please select a user with read permissions on the repository.", "error")
        else:
            flash("Issue saved.", "success")
            db.session.commit()
            return redirect(issue.get_url())

    return render_template("issues/issue.html", issue=issue, repository=repository)
