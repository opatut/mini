from mini.modules.wiki import app, ext
from mini.modules.wiki.models import Page, Tag
from flask import redirect, url_for, render_template

@app.route("/")
@ext.add_menu("wiki", "Wiki")
def index():
    return redirect(url_for("wiki.page", slug="main"))

@app.route("/<slug>")
def page(slug):
    return render_template("page.html", page=Page.query.filter_by(slug=slug).first_or_404())

@app.route("/tag/<tag>")
def tag(tag):
    return render_template("tag.html", tag=Tag.query.filter_by(tag=tag).first_or_404())

@app.route("/tags/")
@ext.add_menu("tags", "Tags", "wiki")
def tags():
    return "lol"
