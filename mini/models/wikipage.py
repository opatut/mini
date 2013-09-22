from mini import db

class WikiPage(db.Model):
    __tablename__ = "wiki_page"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(64), unique=True, default="")
    title = db.Column(db.String(128), default="")
    text = db.Column(db.Text, default="")

    repository = db.relationship("Repository", backref="wiki_pages")
    repository_id = db.Column(db.Integer, db.ForeignKey("repository.id"))
