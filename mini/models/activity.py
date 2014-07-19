from mini import db
from flask import render_template, Markup
from datetime import datetime

class Activity(db.Model):
    __tablename__ = "activity"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    repository_id = db.Column(db.Integer, db.ForeignKey("repository.id"))

    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'activity',
        'polymorphic_on': type
    }

    def __init__(self):
        self.date = datetime.utcnow()

    def render(self, mode="repository"):
        return Markup(render_template("activity/%s.html" % self.type, activity=self, mode=mode))


class PushActivity(Activity):
    __tablename__ = "activity_push"
    id = db.Column(db.Integer, db.ForeignKey("activity.id"), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    commit_ids = db.Column(db.Text)

    @property
    def commits(self):
        return [self.repository.get_commit(cid) for cid in self.commit_ids.split(",") if cid]

class CommentActivity(Activity):
    __tablename__ = "activity_comment"
    id = db.Column(db.Integer, db.ForeignKey("activity.id"), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    issuecomment = db.relationship("IssueComment", backref="activities")
    issuecomment_id = db.Column(db.Integer, db.ForeignKey("issuecomment.id"))

activity_createissue_issue = db.Table('activity_createissue_issue', db.metadata,
    db.Column('activity_id', db.Integer, db.ForeignKey('activity_createissue.id')),
    db.Column('issue_id', db.Integer, db.ForeignKey('issue.id'))
)

class CreateIssueActivity(Activity):
    __tablename__ = "activity_createissue"
    id = db.Column(db.Integer, db.ForeignKey("activity.id"), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    issues = db.relationship("Issue", secondary=activity_createissue_issue) 

class ModifyIssueActivity(Activity):
    __tablename__ = "activity_modifyissue"
    id = db.Column(db.Integer, db.ForeignKey("activity.id"), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    issue = db.relationship("Issue", backref="activities_modify")
    issue_id = db.Column(db.Integer, db.ForeignKey("issue.id"))

    new_status = db.Column(db.Enum("open", "merged", "discussion", "closed", "wip", "invalid", name="activity_creatissue_new_status"))
    new_assignee_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    new_assignee = db.relationship("User", foreign_keys=[new_assignee_id])
    new_tags = db.Column(db.Boolean)

class CreateBranchActivity(Activity):
    __tablename__ = "activity_createbranch"
    id = db.Column(db.Integer, db.ForeignKey("activity.id"), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    branchname = db.Column(db.String(80))

