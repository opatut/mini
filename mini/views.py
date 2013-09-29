from mini import app, access, db
from mini.forms import *
from mini.models import *
from flask import render_template, flash, abort, url_for, request, redirect
from flask.ext.login import current_user
import git # for type checks

@app.context_processor
def inject():
    return dict(REPOSITORY_ROLES=REPOSITORY_ROLES)

################################################################################
# GENERAL                                                                      #
################################################################################

@app.route("/")
def index():
    return redirect(url_for("repositories"))

@app.route("/settings/")
def settings():
    access.check(current_user.has_permission("settings.core"))
    return render_template("account/settings.html")

@app.route("/repositories")
def repositories():
    return render_template("repositories.html", repositories=Repository.query.all())

@app.route("/users")
def users():
    return render_template("users.html", users=User.query.all())

################################################################################
# ACCOUNT                                                                      #
################################################################################

@app.route("/login/", methods=["GET", "POST"])
def login():
    access.check(current_user.has_permission("nologin"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        user.login()
        flash("Welcome back, %s!" % user.username, "success")
        return redirect(url_for("index"))
    elif request.method == "POST":
        flash("Invalid login information, try again.", "error")

    return render_template("account/login.html", form=form)

@app.route("/logout/")
def logout():
    access.check(current_user.has_permission("login"))
    current_user.logout()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/register/")
def register():
    access.check(current_user.has_permission("nologin"))
    abort(501)
    #return render_template("register.html")

@app.route("/settings/", methods=("GET", "POST"))
@app.route("/settings/<tab>/", methods=("GET", "POST"))
def settings(tab="general"):
    access.check(current_user.has_permission("login"))
    args = {}

    if tab == "general":
        form = GeneralSettingsForm(obj=current_user)
        password_form = ChangePasswordForm()

        if form.validate_on_submit():
            form.populate_obj(current_user)
            db.session.commit()
            flash("Your settings were saved.", "success")
            return redirect(url_for("settings", tab="general"))
        elif password_form.validate_on_submit():
            if hash_password(password_form.password.data) != current_user.password:
                flash("Your old password is incorrect. Please try again.", "error")
            else:
                current_user.password = hash_password(password_form.password1.data)
                db.session.commit()
                flash("You changed your password.", "success")
                return redirect(url_for("settings", tab="general"))

        args["form"] = form
        args["password_form"] = password_form

    elif tab == "emails":
        form = NewEmailForm()
        if form.validate_on_submit():
            email = Email()
            email.user = current_user
            email.email = form.email.data
            db.session.add(email)
            db.session.commit()

        args["form"] = form

    elif tab == "keys":
        form = NewPublicKeyForm()
        if form.validate_on_submit():
            key = PublicKey()
            key.set_key(form.key.data)
            key.name = form.name.data.strip()
            key.user = current_user
            db.session.add(key)
            db.session.commit()
            flash("Your key was added. Please check the fingerprint: <code>%s</code>." % key.fingerprint, "success")
            return redirect(url_for("settings", tab="keys"))

        args["form"] = form

    elif tab == "notifications":
        pass

    else:
        abort(404)

    return render_template("account/settings.html", tab=tab, **args)

@app.route("/settings/emails/<id>/<action>/")
def settings_email_action(action, id):
    access.check(current_user.has_permission("login"))
    email = Email.query.filter_by(id=id).first_or_404()

    if email.user != current_user:
        abort(403)

    if action == "set-gravatar":
        for m in current_user.emails: m.is_gravatar = (m == email)
        flash("Your email settings were successfully updated.", "success")
    elif action == "set-default":
        for m in current_user.emails: m.is_default = (m == email)
        flash("Your email settings were successfully updated.", "success")
    elif action == "remove":
        if email.is_default or email.is_gravatar:
            flash("Cannot remove default or gravatar address.", "error")
        else:
            db.session.delete(email)
            flash("The email address %s has been removed." % email.email, "success")
    else:
        abort(404)

    db.session.commit()
    return redirect(url_for("settings", tab="emails"))

@app.route("/user/<username>")
def user(username=""):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("account/profile.html", user=user)

################################################################################
# HISTORY                                                                      #
################################################################################

@app.route("/<slug>/")
def repository(slug):
    return redirect(url_for("browse", slug=slug))

@app.route("/<slug>/history/")
def history(slug):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.has_permission(current_user, "read"))
    return render_template("repository/content/history.html", repository=repository)

@app.route("/<slug>/history/<rev>/")
def commit(slug, rev):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.has_permission(current_user, "read"))

    commit = repository.get_commit(rev)
    return render_template("repository/content/commit.html", repository=repository, commit=commit, rev=rev)

################################################################################
# BROWSE                                                                       #
################################################################################

@app.route("/<slug>/browse/")
@app.route("/<slug>/browse/<rev>/")
@app.route("/<slug>/browse/<rev>/<path:path>")
def browse(slug, rev="", path=""):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.has_permission(current_user, "read"))

    if not rev:
        if len(repository.git.heads):
            rev = repository.git.heads[0].name
        else:
            return render_template("repository/content/empty.html", repository=repository)
    path = path.rstrip("/")

    commit = repository.get_commit(rev)
    if not commit:
        flash("Invalid revision: %s." % rev, "error")
        return redirect(url_for("repository", slug=repository.slug))

    target = commit.tree
    if path:
        target = target / path

    if isinstance(target, git.Blob):
        return render_template("repository/content/file.html", repository=repository, file=target, commit=commit, rev=rev, path=path)
    elif isinstance(target, git.Tree):
        return render_template("repository/content/browse.html", repository=repository, tree=target, commit=commit, rev=rev, path=path)
    else:
        raise exception("should reaaally never happen.")

@app.route("/<slug>/raw/<rev>/<path:path>")
def file_content(slug, rev, path):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.has_permission(current_user, "read"))

    commit = repository.get_commit(rev)
    if not commit: abort(404)

    blob = commit.tree / path
    response = main_app.make_response(blob.data_stream.read())
    response.mimetype = blob.mime_type
    return response

################################################################################
# REPOSITORY ADMIN                                                             #
################################################################################

@app.route("/repositories/new", methods=("GET", "POST"))
def repository_new():
    access.check(current_user.has_permission("repository.create"))
    form = RepositoryCreateForm()
    if form.validate_on_submit():
        repository = Repository()
        form.populate_obj(repository)
        if form.clone.data and not repository.clone_from(form.clone.data):
            flash("Could not clone the upstream repository.", "error")
        elif not form.clone.data and not repository.init():
            flash("Failed to initialize repository. Ask an admin about this!", "error")
        else:
            repository.set_permission(current_user, "admin")
            db.session.add(repository)
            db.session.commit()
            flash("Repository created.", "success")
            return redirect(url_for("repository", slug=repository.slug))
    return render_template("repository/new.html", form=form)

@app.route("/<slug>/admin/", methods=("GET", "POST"))
@app.route("/<slug>/admin/<tab>", methods=("GET", "POST"))
def admin(slug, tab="general"):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.has_permission(current_user, "admin"))

    args = {}

    if tab == "general":
        form = RepositorySettingsForm(obj=repository)
        form.set_repository(repository)
        args["form"] = form

        if form.validate_on_submit():
            if form.slug.data != repository.slug:
                repository.move_to(form.slug.data)
                flash("Your repository has been moved to %s. Please update your remotes." % form.slug.data, "warning")
            form.populate_obj(repository)
            db.session.commit()
            flash("Repository settings have been saved.", "success")
            return redirect(url_for("admin", slug=repository.slug, tab="general"))
    elif tab == "tags":
        tags = IssueTag.query.filter_by(repository_id=repository.id).all()
        args["tags"] = tags

        tag = None
        if "edit-tag" in request.args:
            tag = IssueTag.query.filter_by(tag=request.args.get("edit-tag")).first()
            args["edit_tag"] = tag
        elif "remove-tag" in request.args:
            tag = IssueTag.query.filter_by(tag=request.args.get("remove-tag")).first_or_404()
            db.session.delete(tag)
            db.session.commit()
            flash("Tag %s deleted."%tag.tag, "success")
            return redirect(url_for("admin", slug=repository.slug, tab="tags"))


        form = TagForm(obj=tag)
        if form.validate_on_submit():
            if not tag:
                edit_tag = IssueTag()
                edit_tag.repository = repository
                db.session.add(edit_tag)
            else:
                edit_tag = tag
            form.populate_obj(edit_tag)
            db.session.commit()
            if tag:
                flash("Tag %s updated." % edit_tag.tag, "success")
            else:
                flash("Tag %s added." % edit_tag.tag, "success")
            return redirect(url_for("admin", slug=repository.slug, tab="tags"))
        args["form"] = form
    elif tab == "permissions":
        form = AddPermissionForm()
        args["form"] = form

        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if not user:
                flash("Username not found. Please enter the nickname, not the real name!", "error")
            elif not repository.set_permission(user, form.access.data):
                flash("You cannot add yourself to this list!", "error")
            else:
                flash("Permission %s for user %s added." % (user.get_display_name(), form.access.data), "success")
                return redirect(url_for("admin", slug=slug))
    else:
        abort(404)

    return render_template("repository/admin/admin.html", repository=repository, tab=tab, **args)

@app.route("/<slug>/admin/permission/<id>/<level>/")
def admin_set_permission(slug, id, level):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.has_permission(current_user, "admin"))

    user = (None if (id==0) else User.query.filter_by(id=id).first())

    if level == "remove" and user:
        permission = repository.get_explicit_permission(user)
        if permission:
            db.session.delete(permission)
            db.session.commit()
        flash("The permission level has been removed.", "success")
    elif level in REPOSITORY_ROLES:
        if not repository.set_permission(user, level):
            flash("You cannot change your own permissions, sorry. Make someone else admin for that!", "error")
        else:
            flash("The permission level has been changed.", "success")
    else:
        abort(404)
    return redirect(url_for("admin", slug=slug))

################################################################################
# ISSUES                                                                       #
################################################################################

@app.route("/<slug>/issues/")
def issues(slug):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.has_permission(current_user, "read"))
    return render_template("repository/issues/issues.html", issues=repository.issues, repository=repository)

@app.route("/<slug>/issues/<number>", methods=("GET", "POST"))
def issue(slug, number):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.has_permission(current_user, "read"))
    issue = Issue.query.filter_by(repository_id=repository.id, number=number).first_or_404()

    args = {}

    if request.method == "POST" and "save-status" in request.args:
        access.check(issue.can_edit(current_user))
        issue.status = request.form.get("status")
        assignee_id = request.form.get("assignee")
        issue.assignee = User.query.filter_by(id=assignee_id).first() if assignee_id else None
        issue.issue_tags = [tag for tag in repository.issue_tags if str(tag.id) in request.form.getlist("tag")]

        if not issue.status in ("open", "discussion", "wip", "invalid", "closed"):
            flash("Please select a valid issue state.", "error")
        elif issue.assignee and not repository.has_permission(issue.assignee, "read"):
            flash("Please select a user with read permissions on the repository.", "error")
        else:
            flash("Issue saved.", "success")
            db.session.commit()
            return redirect(issue.get_url())
    elif request.method == "POST" and "post-comment" in request.args:
        access.check(issue.can_comment(current_user))
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
    elif "edit-comment" in request.args:
        comment = IssueComment.query.filter_by(id=request.args.get("edit-comment")).first_or_404()
        access.check(comment.can_edit(current_user))
        form = EditCommentForm(obj=comment)
        args["form_comment"] = form
        args["edit_comment_id"] = comment.id
        if form.validate_on_submit():
            form.populate_obj(comment)
            db.session.commit()
            flash("The comment has been saved.", "success")
            return redirect(issue.get_url() + "#comment-%s" % comment.id)
    elif request.method == "GET" and "remove-comment" in request.args:
        comment = IssueComment.query.filter_by(id=request.args.get("remove-comment")).first_or_404()
        access.check(comment.can_delete(current_user))
        if not comment.issue == issue:
            abort(404)
        db.session.delete(comment)
        db.session.commit()
        flash("Comment removed.", "success")
        return redirect(issue.get_url())

    return render_template("repository/issues/issue.html", repository=repository, issue=issue, action="view", **args)

@app.route("/<slug>/issues/<number>/edit", methods=("GET", "POST"))
def issue_edit(slug, number):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.has_permission(current_user, "comment"))
    issue = Issue.query.filter_by(repository_id=repository.id, number=number).first_or_404()
    access.check(issue.can_edit(current_user))

    form = EditIssueForm(obj=issue)

    if form.validate_on_submit():
        form.populate_obj(issue)
        db.session.commit()
        flash("The issue was updated.", "success")
        return redirect(url_for("issue", slug=repository.slug, number=issue.number))

    return render_template("repository/issues/issue.html", repository=repository, issue=issue, form=form, action="edit")

@app.route("/<slug>/issues/new", methods=("GET", "POST"))
def issue_new(slug):
    access.check(current_user.has_permission("login"))
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.has_permission(current_user, "comment"))

    form = EditIssueForm()
    if form.validate_on_submit():
        issue = Issue()
        form.populate_obj(issue)
        issue.number = repository.next_issue_number
        repository.next_issue_number += 1
        issue.status = "open"
        issue.author = current_user
        issue.repository = repository
        db.session.add(issue)
        db.session.commit()
        flash("Your issue was created.", "success")
        return redirect(url_for("issue", slug=repository.slug, number=issue.number))

    return render_template("repository/issues/new.html", repository=repository, form=form)

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
    access.check(repository.has_permission(current_user, "read"))
    wikipage = WikiPage.query.filter_by(slug=page).first_or_404()
    return render_template("repository/wiki/page.html", repository=repository, page=wikipage, action="view")

@app.route("/<slug>/wiki/<page>/edit", methods=("POST", "GET"))
def wiki_edit(slug, page=""):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.has_permission(current_user, "write"))
    wikipage = WikiPage.query.filter_by(slug=page).first_or_404()
    return wiki_page_form(repository, wikipage, "edit")

@app.route("/<slug>/wiki/<page>/delete", methods=("POST", "GET"))
def wiki_delete(slug, page=""):
    repository = Repository.query.filter_by(slug=slug).first_or_404()
    access.check(repository.has_permission(current_user, "write"))
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
    access.check(repository.has_permission(current_user, "write"))
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

    return render_template("repository/wiki/page.html", repository=repository, page=wikipage, form=form, action=action)
