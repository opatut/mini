# -*- coding: utf-8 -*-

import os
import git # GitPython
from os.path import *
from datetime import datetime, timedelta
from hashlib import sha512, md5
from minigit import app, db
from minigit.util import *
from flask import url_for, Markup
from minigit.login import *

class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(80), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    is_default = db.Column(db.Boolean)
    is_gravatar = db.Column(db.Boolean)

    def __init__(self, address, user):
        self.address = address
        self.user = user

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique = True)
    password = db.Column(db.String(128))

    emails = db.relationship("Email", backref = "user", lazy = "dynamic")

    is_admin = db.Column(db.Boolean, default = False)
    permissions = db.relationship("Permission", backref = "user", lazy = "dynamic")

    def __init__(self, username, password):
        self.username = username
        self.password = hash_password(password)

    def addEmail(self, email, default = False, gravatar = False):
        e = Email(email, self)
        db.session.add(e)
        self.emails.append(e)

        if default: self.setDefaultEmail(e)
        if gravatar: self.setGravatarEmail(e)

    def setDefaultEmail(self, email):
        if self.default_email:
            if self.default_email == email:
                return
            self.default_email.is_default = False
        email.is_default = True

    def setGravatarEmail(self, email):
        if self.gravatar_email:
            if self.gravatar_email == email:
                return
            self.gravatar_email.is_gravatar = False
        email.is_gravatar = True

    @property
    def default_email(self):
        return Email.query.filter_by(user_id = self.id, is_default = True).first()

    @property
    def gravatar_email(self):
        return Email.query.filter_by(user_id = self.id, is_gravatar = True).first()


    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def url(self, **values):
        return url_for('profile', username = self.username, **values)

    @property
    def link(self):
        return Markup('<a href="{0}">{1}</a>'.format(self.url, self.username))

    def getAvatar(self, size = 32):
        # get gravatar email
        email = self.gravatar_email
        if not email: email = self.default_email

        return "http://www.gravatar.com/avatar/{0}?s={1}&d=identicon".format(md5(email.address.lower()).hexdigest(), size)

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    repository_id = db.Column(db.Integer, db.ForeignKey("repository.id"))
    access = db.Column(db.Enum("none", "find", "read", "write", "admin"), default = "none")

    def __init__(self, user, repository, access):
        self.user = user
        self.repository = repository
        self.access = access

