from mini.modules.core import app, ext
from mini.modules.core.forms import LoginForm
from mini.modules.core.models import User
from flask import render_template, flash, abort, url_for, request, redirect
from flask.ext.login import current_user

@app.route("/")
@ext.menu.add_view("index", "Index", index=-100)
def index():
    from mini import core
    return render_template("index.html", widgets=core.widgets)

@app.route("/settings/")
@ext.menu.add_view("settings", "Settings", index=100)
@ext.access.require("settings.core")
def settings():
    return render_template("settings.html")

@app.route("/login/", methods=["GET", "POST"])
@ext.menu.add_view("login", "Login", index=200)
@ext.access.require("nologin")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        user.login()
        flash("Welcome back, %s!" % user.username, "success")
        return redirect(url_for("core.index"))
    elif request.method == "POST":
        flash("Invalid login information, try again.", "error")

    return render_template("login.html", form=form)

@app.route("/logout/")
@ext.menu.add_view("logout", "Logout", "account", index=100)
@ext.access.require("login")
def logout():
    current_user.logout()
    flash("You have been logged out.", "info")
    return redirect(url_for("core.index"))

@app.route("/account/")
@ext.menu.add_view("account", "Account", index=200)
@ext.access.require("login")
def account():
    return render_template("settings.html")

@app.route("/p/<p>")
def permission(p):
    from mini import access
    return str(access.user_has_permission(p))
