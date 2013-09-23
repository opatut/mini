from mini import app, menu, access, db
from mini.forms import *
from mini.models import *
from flask import render_template, flash, abort, url_for, request, redirect
from flask.ext.login import current_user
import git # for type checks

################################################################################
# GENERAL                                                                      #
################################################################################

@app.route("/")
@menu.add_view("index", "Index", index=-100)
def index():
    return redirect(url_for("repositories"))
    #return render_template("index.html")

@app.route("/settings/")
@menu.add_view("settings", "Settings", index=100)
@access.require("settings.core")
def settings():
    return render_template("settings.html")

@app.route("/repositories")
@menu.add_view("repositories", "Repositories", "index")
def repositories():
    return render_template("git/repositories.html", repositories=Repository.query.all())

################################################################################
# ACCOUNT                                                                      #
################################################################################

@app.route("/login/", methods=["GET", "POST"])
@menu.add_view("login", "Login", index=200)
@access.require("nologin")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        user.login()
        flash("Welcome back, %s!" % user.username, "success")
        return redirect(url_for("index"))
    elif request.method == "POST":
        flash("Invalid login information, try again.", "error")

    return render_template("login.html", form=form)

@app.route("/logout/")
@menu.add_view("logout", "Logout", "account", index=100)
@access.require("login")
def logout():
    current_user.logout()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/account/")
@menu.add_view("account", "Account", index=200)
@access.require("login")
def account():
    return render_template("settings.html")

################################################################################
# HISTORY                                                                      #
################################################################################

@app.route("/<slug>/")
def repository(slug):
    return redirect(url_for("browse", slug=slug))

@app.route("/<slug>/history/")
def history(slug):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("read"))
    return render_template("git/history.html", repository=repository)

@app.route("/<slug>/history/<rev>/")
def commit(slug, rev):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("read"))

    commit = repository.get_commit(rev)
    return render_template("git/commit.html", repository=repository, commit=commit, rev=rev)

################################################################################
# BROWSE                                                                       #
################################################################################

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

################################################################################
# ADMIN                                                                        #
################################################################################

@app.route("/<slug>/admin")
def admin(slug):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("admin"))
    return render_template("admin.html", repository=repository)

################################################################################
# ISSUES                                                                       #
################################################################################

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
    elif request.method == "POST" and "post-comment" in request.args:
        comment = IssueComment()
        comment.author = current_user
        comment.issue = issue
        comment.text = request.form.get("comment")
        if comment.text:
            db.session.add(comment)
            db.session.commit()
            flash("Comment saved.", "success")
            return redirect(issue.get_url())
        else:
            flash("Please insert a comment.", "error")
    elif request.method == "GET" and "comment-remove" in request.args:
        comment = IssueComment.query.filter_by(id=request.args.get("comment-remove")).first_or_404()
        if not comment.can_delete(current_user):
            abort(403)
        elif not comment.issue == issue or not (comment.author == current_user or access.has_permission(repository.get_permission("admin"))):
            flash("You don't have permission to remove this comment.", "error")
        else:
            db.session.delete(comment)
            db.session.commit()
            flash("Comment removed.", "success")
            return redirect(issue.get_url())

    return render_template("issues/issue.html", issue=issue, repository=repository)

################################################################################
# WIKI                                                                         #
################################################################################

@app.route("/<slug>/wiki/")
def wiki(slug):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    if not repository.wiki_pages: return redirect(url_for("wiki_new", slug=slug))
    return redirect(url_for("wiki_page", slug=slug, page=repository.wiki_pages[0].slug))

@app.route("/<slug>/wiki/<page>")
def wiki_page(slug, page=""):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("read"))
    wikipage = WikiPage.query.filter_by(slug=page).first_or_404()
    return render_template("wiki/page.html", repository=repository, page=wikipage, action="view")

@app.route("/<slug>/wiki/<page>/edit", methods=("POST", "GET"))
def wiki_edit(slug, page=""):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("write"))
    wikipage = WikiPage.query.filter_by(slug=page).first_or_404()
    return wiki_page_form(repository, wikipage, "edit")

@app.route("/<slug>/wiki/<page>/delete", methods=("POST", "GET"))
def wiki_delete(slug, page=""):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("write"))
    wikipage = WikiPage.query.filter_by(slug=page).first_or_404()
    for child in wikipage.child_pages:
        child.parent_page = wikipage.parent_page
    db.session.delete(wikipage)
    db.session.commit()
    flash("The wiki page was deleted.", "success")
    return redirect(wikipage.parent_page.get_url() if wikipage.parent_page else url_for("wiki", slug=slug))

@app.route("/<slug>/wiki/new", methods=("POST", "GET"))
def wiki_new(slug):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.get_permission("write"))
    wikipage = WikiPage()
    wikipage.repository = repository
    return wiki_page_form(repository, wikipage, "new")

def wiki_page_form(repository, wikipage, action):
    form = WikiPageForm(obj=wikipage)
    form.init_parent(wikipage)

    if form.validate_on_submit():
        form.populate_obj(wikipage)
        if not generate_new_slug(wikipage):
            flash("This title is similar to a title already used. Please choose a different title.", "error")
        else:
            db.session.commit()
            if action == "new":
                flash("The page was created.", "success")
            else:
                flash("The changes made to the page were saved.", "success")
            return redirect(wikipage.get_url())

    return render_template("wiki/page.html", repository=repository, page=wikipage, form=form, action=action)
