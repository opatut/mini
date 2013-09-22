from mini import db
from flask import Markup

issue_tag = db.Table('issue_issuetag', db.metadata,
    db.Column('issue_id', db.Integer, db.ForeignKey('issue.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('issue_tag.id'))
)

class IssueTag(db.Model):
    __tablename__ = "issue_tag"
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(64), unique=True)
    color = db.Column(db.String(6))

    repository = db.relationship("Repository", backref="issue_tags")
    repository_id = db.Column(db.Integer, db.ForeignKey("repository.id"))

    issues = db.relationship("Issue", backref="issue_tags", secondary="issue_issuetag")

    def get_url(self):
        return "#TODO"

    def render(self):
        return Markup('<a href="{url}" class="issuetag label" style="background: #{color};">{tag}</a>'
            .format(url=self.get_url(), color=self.color, tag=self.tag))
