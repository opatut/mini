from mini import db
from flask import Markup
from mini.util import hex_to_rgb_float, rgb_brightness

issue_tag = db.Table('issue_issuetag', db.metadata,
    db.Column('issue_id', db.Integer, db.ForeignKey('issue.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('issue_tag.id'))
)

class IssueTag(db.Model):
    __tablename__ = "issue_tag"
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(64))
    color = db.Column(db.String(6))

    repository = db.relationship("Repository", backref="issue_tags")
    repository_id = db.Column(db.Integer, db.ForeignKey("repository.id"))

    issues = db.relationship("Issue", backref="issue_tags", secondary="issue_issuetag")

    def get_url(self):
        return "#TODO"

    def render(self):
        return Markup('<a href="{url}" class="issuetag label {text_color_class}" style="background: #{color};">{tag}</a>'
            .format(url=self.get_url(), color=self.color, tag=self.tag, text_color_class=self.text_color_class))

    @property
    def text_color_class(self):
        return "light" if rgb_brightness(*hex_to_rgb_float(self.color)) < 0.8 else "dark"
