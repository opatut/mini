# -*- coding: utf-8 -*-

from mini import db, login_manager
from mini.util import *
from mini.models.email import Email
from mini.models.team import Member
from datetime import datetime
from flask.ext.login import current_user, login_user, logout_user
from flask import url_for
import fnmatch

class User(Member, AnonymousUser):
    __tablename__ = "user"
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = db.Column(db.Integer, db.ForeignKey("member.id"), primary_key = True)
    password = db.Column(db.String(128))
    created = db.Column(db.DateTime)

    status = db.Column(db.Enum("unverified", "normal", "banned"), default="normal")
    verify_hash = db.Column(db.String(80))

    permissions = db.Column(db.Text)
    restrictions = db.Column(db.Text)

    location = db.Column(db.String(200))
    about = db.Column(db.Text)

    activities = db.relationship("Activity", backref="user", lazy="dynamic")

    def __init__(self):
        self.created = datetime.utcnow()

    def set_password(self, cleartext):
        self.password = hash_password(cleartext)

    def generate_verify_hash(self):
        self.verify_hash = random_string(10)
        return self.verify_hash

    @property
    def default_email(self):
        return Email.query.filter_by(user_id=self.id, is_default=True).first()

    @property
    def gravatar_email(self):
        return Email.query.filter_by(user_id=self.id, is_gravatar=True).first()

    def get_avatar(self, size=32):
        return self.gravatar_email.get_avatar(size)

    def has_permission(self, permission):
        if permission == "login":
            return True

        if permission == "nologin":
            return False

        if not self.permissions: return False

        for line in self.permissions.splitlines():
            if line and fnmatch.fnmatch(permission, line):
                return True

        # for team in self.teams:
        #     if team.has_permission(permission):
        #         return True

        return False

    def get_display_name(self):
        return self.name if self.name else self.identifier

    def get_link(self, size=16):
        return Markup('<span class="user"><a href="{2}"><img class="avatar" src="{0}" /></a> <a href="{2}">{1}</a></span>'.format(self.get_avatar(size), self.get_display_name(), self.get_url()))

    def get_url(self):
        return url_for("user", identifier=self.identifier)

    def get_owned_repositories(self):
        from mini.models import Repository, Permission
        return Repository.query.join(Permission).filter_by(member_id=self.id, access="admin")

    @staticmethod
    def get_current():
        return current_user

# we need this so flask-login can load a user into a session
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()
