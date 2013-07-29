# -*- coding: utf-8 -*-

from mini import db, login_manager
from mini.base.util import *
from datetime import datetime
from flask.ext.login import current_user, login_user, logout_user
import fnmatch

class AnonymousUser(object):
    def has_permission(self, permission):
        return permission == "nologin"

    def get_id(self):
        return unicode(0)

    def is_active(self):
        return False

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return False

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique = True)
    password = db.Column(db.String(128))
    created = db.Column(db.DateTime)
    permissions = db.Column(db.Text)

    def __init__(self):
        self.created = datetime.utcnow()

    def set_password(self, cleartext):
        self.password = hash_password(cleartext)

    def get_avatar(self, size = 32):
        return "http://www.gravatar.com/avatar/{0}?s={1}&d=identicon".format(md5(self.email.address.lower()).hexdigest(), size)

    def has_permission(self, permission):
        if permission == "login":
            return True

        if permission == "nologin":
            return False

        for line in self.permissions.splitlines():
            if line and fnmatch.fnmatch(permission, line):
                return True

        return False

    def login(self):
        login_user(self)

    def logout(self):
        logout_user()

    @staticmethod
    def get_current():
        return current_user

    # flask-login
    def get_id(self):
        return unicode(self.id)

    def is_active(self):
        return True #self.is_verified

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True
    # /flask-login

# we need this so flask-login can load a user into a session
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()
