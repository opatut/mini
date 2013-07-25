# -*- coding: utf-8 -*-

from mini import db
from mini.base.util import *
from datetime import datetime
import fnmatch

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
