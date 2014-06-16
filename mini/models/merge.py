from mini import db
from flask import url_for
from datetime import datetime
from issue import Issue

class Merge(Issue):
    __tablename__ = "merge"
    __mapper_args__ = {
        'polymorphic_identity': 'merge'
    }

    id = db.Column(db.Integer, db.ForeignKey("issue.id"), primary_key=True)

    from_repository_id = db.Column(db.Integer, db.ForeignKey("repository.id"))
    from_repository = db.relationship("Repository", backref="merges_from", foreign_keys=[from_repository_id])
    from_rev = db.Column(db.String(80))

    # repository mapping exists in issue
    rev = db.Column(db.String(80))
