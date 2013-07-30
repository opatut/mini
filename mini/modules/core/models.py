# -*- coding: utf-8 -*-

from mini import db, login_manager
from mini.base.util import *
from datetime import datetime
from flask.ext.login import current_user, login_user, logout_user
import fnmatch

class User(db.Model, AnonymousUser):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), unique = True)
    username = db.Column(db.String(80), unique = True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(128))
    created = db.Column(db.DateTime)
    permissions = db.Column(db.Text)

    def __init__(self):
        self.created = datetime.utcnow()

    def set_password(self, cleartext):
        self.password = hash_password(cleartext)

    def get_avatar(self, size = 32):
        return "http://www.gravatar.com/avatar/{0}?s={1}&d=identicon".format(md5(self.email.lower()).hexdigest(), size)

    def has_permission(self, permission):
        if permission == "login":
            return True

        if permission == "nologin":
            return False

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
