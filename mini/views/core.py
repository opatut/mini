from mini import app, menu, access
from mini.forms import LoginForm
from mini.models import User
from flask import render_template, flash, abort, url_for, request, redirect
from flask.ext.login import current_user

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
