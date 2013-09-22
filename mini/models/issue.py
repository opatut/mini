from mini import db
from flask import url_for

class Issue(db.Model):
    __tablename__ = "issue"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    title = db.Column(db.String(128), default="")
    text = db.Column(db.Text, default="")
    status = db.Column(db.Enum("open", "discussion", "closed", "wip", "invalid"), default="open")

    assignee = db.relationship("User", backref="assigned_issues")
    assignee_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    repository = db.relationship("Repository", backref="issues")
    repository_id = db.Column(db.Integer, db.ForeignKey("repository.id"))

    def get_url(self):
        return url_for("issue", slug=self.repository.slug, number=self.number)
