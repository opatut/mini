from mini.modules.wiki import app, ext
from mini.modules.wiki.models import Page, Tag
from flask import redirect, url_for, render_template

@app.route("/")
@ext.menu.add_view("wiki", "Wiki")
def index():
    return redirect(url_for("wiki.page", slug="main"))

@app.route("/<slug>")
@app.route("/<slug>/<action>")
@ext.menu.add_view("new", "New Page", "wiki", slug="new")
def page(slug, action="view"):
    if slug == "new":
        action = "new"
        page = Page()
    else:
        page = Page.query.filter_by(slug=slug).first_or_404()

    return render_template("page.html", page=page, action=action)

@app.route("/tag/<tag>")
def tag(tag):
    return render_template("tag.html", tag=Tag.query.filter_by(tag=tag).first_or_404())

@app.route("/tags/")
@ext.menu.add_view("tags", "Tags", "wiki")
def tags():
    return "lol"

@app.route("/settings/")
@ext.menu.add_view("wiki", "Wiki", "settings")
def settings():
    return "lol"
