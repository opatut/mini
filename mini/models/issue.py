from mini import db
from flask import url_for
from datetime import datetime

class Issue(db.Model):
    __tablename__ = "issue"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)
    number = db.Column(db.Integer)
    title = db.Column(db.String(128), default="")
    text = db.Column(db.Text, default="")
    status = db.Column(db.Enum("open", "discussion", "closed", "wip", "invalid"), default="open")

    assignee_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    assignee = db.relationship("User", backref="assigned_issues", foreign_keys=[assignee_id])

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", backref="authored_issues", foreign_keys=[author_id])

    repository = db.relationship("Repository", backref="issues")
    repository_id = db.Column(db.Integer, db.ForeignKey("repository.id"))

    def __init__(self):
        self.created = datetime.utcnow()

    def get_url(self):
        return url_for("issue", slug=self.repository.slug, number=self.number)

    def get_sorted_comments(self):
        comments = list(self.issue_comments)
        comments.sort(key=lambda comment: comment.created)
        return comments

    def can_edit(self, user):
        return user == self.author or user.has_permission(self.repository.get_permission("write"))
