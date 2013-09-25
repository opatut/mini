# -*- coding: utf-8 -*-

from mini import db, login_manager
from mini.util import *
from mini.models import Email
from datetime import datetime
from flask.ext.login import current_user, login_user, logout_user
import fnmatch

class User(db.Model, AnonymousUser):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), unique = True)
    username = db.Column(db.String(80), unique = True)
    password = db.Column(db.String(128))
    created = db.Column(db.DateTime)

    permissions = db.Column(db.Text)
    restrictions = db.Column(db.Text)

    location = db.Column(db.String(200))
    about = db.Column(db.Text)

    def __init__(self):
        self.created = datetime.utcnow()

    def set_password(self, cleartext):
        self.password = hash_password(cleartext)

    @property
    def default_email(self):
        return Email.query.filter_by(user_id=self.id, is_default=True).first()

    @property
    def gravatar_email(self):
        return Email.query.filter_by(user_id=self.id, is_gravatar=True).first()

    def get_avatar(self, size=32):
        return self.gravatar_email.get_avatar(size)

    def has_permission(self, permission):
        if permission == "logged-in":
            return True

        if permission == "not-logged-in":
            return False

        if not self.permissions: return False

        for line in self.permissions.splitlines():
            if line and fnmatch.fnmatch(permission, line):
                return True

        return False

    def get_display_name(self):
        return self.name or self.username

    def get_link(self):
        return Markup('<span class="user"><a href="{2}"><img class="avatar" src="{0}" /></a> {1}</span>'.format(self.get_avatar(16), self.get_display_name(), self.get_url()))

    def get_url(self):
        return "#TODO"

    @staticmethod
    def get_current():
        return current_user

# we need this so flask-login can load a user into a session
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()
