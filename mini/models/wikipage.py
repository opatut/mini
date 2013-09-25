from mini import db
from flask import url_for

class WikiPage(db.Model):
    __tablename__ = "wiki_page"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(64), unique=True, default="")
    title = db.Column(db.String(128), default="")
    text = db.Column(db.Text, default="")

    repository = db.relationship("Repository", backref="wiki_pages")
    repository_id = db.Column(db.Integer, db.ForeignKey("repository.id"))

    parent_page = db.relationship("WikiPage", backref="child_pages", remote_side=[id])
    parent_page_id = db.Column(db.Integer, db.ForeignKey("wiki_page.id"))

    def get_url(self):
        return url_for("wiki_page", slug=self.repository.slug, page=self.slug)

    def can_edit(self, user):
        return self.repository.has_permission(user, "write")
