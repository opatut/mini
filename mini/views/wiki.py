from mini import app, menu, access
from mini.models import WikiPage
from flask import redirect, url_for, render_template

@app.route("/<repository_slug>/wiki/<slug>")
@app.route("/<repository_slug>/wiki/<slug>/<action>")
@menu.add_view("new", "New Page", "wiki", slug="new")
def page(repository_slug, slug, action="view"):
    if slug == "new":
        action = "new"
        page = WikiPage()
    else:
        page = WikiPage.query.filter_by(slug=slug).first_or_404()

    return render_template("wiki/page.html", page=page, action=action)
