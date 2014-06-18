from mini import db
from flask import url_for, Markup
from datetime import datetime

class Issue(db.Model):
    __tablename__ = "issue"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    created = db.Column(db.DateTime)
    number = db.Column(db.Integer)
    title = db.Column(db.String(128), default="")
    text = db.Column(db.Text, default="")
    status = db.Column(db.Enum("open", "merged", "discussion", "closed", "wip", "invalid", name="issue_status"), default="open")

    assignee_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    assignee = db.relationship("User", backref="assigned_issues", foreign_keys=[assignee_id])

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", backref="authored_issues", foreign_keys=[author_id])

    repository_id = db.Column(db.Integer, db.ForeignKey("repository.id"))

    __mapper_args__ = {
        'polymorphic_identity': 'issue',
        'polymorphic_on': type
    }

    def __init__(self):
        self.created = datetime.utcnow()

    def get_link(self):
        return Markup('<span class="{0}"><a href="{2}">{1}</a></span>'.format(self.type, self.title, self.get_url()))

    def get_url(self):
        return url_for(self.type, slug=self.repository.slug, number=self.number)

    def get_sorted_comments(self):
        comments = list(self.issue_comments)
        comments.sort(key=lambda comment: comment.created)
        return comments

    def can_edit(self, user):
        return not user.is_anonymous() and (user == self.author or self.repository.has_permission(user, "mod"))

    def can_comment(self, user):
        return not user.is_anonymous() and (user == self.author or self.repository.has_permission(user, "comment"))

    def get_status_icon(self):
        return {"open": "circle-o", 
            "closed":"check-circle-o", 
            "invalid":"ban", 
            "wip":"circle-o", 
            "merged":"check-circle-o", 
            "rejected":"ban",
            "discussion":"circle-o"}[self.status]
