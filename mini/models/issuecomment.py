from mini import db
from flask import url_for
from datetime import datetime

class IssueComment(db.Model):
    __tablename__ = "issuecomment"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, default="")
    created = db.Column(db.DateTime)

    issue = db.relationship("Issue", backref="issue_comments", order_by="IssueComment.created")
    issue_id = db.Column(db.Integer, db.ForeignKey("issue.id"))

    author = db.relationship("User", backref="issue_comments")
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self):
        self.created = datetime.utcnow()

    def can_edit(self, user):
        return user == self.author or self.issue.repository.has_permission(user, "write")

    def can_delete(self, user):
        return self.can_edit(user) and self.issue.issue_comments[-1] == self
