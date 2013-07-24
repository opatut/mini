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

class PublicKey(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    key = db.Column(db.String(1024), unique = True)
    name = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, key, name, user):
        self.key = key.strip()
        self.name = name
        self.user = user

    @property
    def fingerprint(self):
        return fingerprint(self.key)

    @property
    def type(self):
        return keytype(self.key)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique = True)
    password = db.Column(db.String(128))

    emails = db.relationship("Email", backref = "user", lazy = "dynamic")
    keys = db.relationship("PublicKey", backref = "user", lazy = "dynamic")

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

    def addPublicKey(self, key, name = ""):
        if not verify_key(key):
            raise Error("Invalid SSH Key.")
        k = PublicKey(key, name, self)
        db.session.add(k)
        self.keys.append(k)

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

class Repository(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    slug = db.Column(db.String(128), unique = True)
    title = db.Column(db.String(128))
    upstream = db.Column(db.String(256)) # URL BRANCH
    is_public = db.Column(db.Boolean, default = True)
    implicit_access = db.Column(db.Enum("none", "find", "read", "write", "admin"), default = "none")
    implicit_guest_access = db.Column(db.Boolean, default = False)
    created = db.Column(db.DateTime)

    permissions = db.relationship("Permission", backref = "repository", lazy = "dynamic")

    _git = None
    _commits = None
    _contributors = None

    def __init__(self, title, slug = ""):
        self.slug = get_slug(title) if not slug else slug
        self.title = title
        self.created = datetime.utcnow()

    @property
    def path(self):
        return abspath(join(app.config["REPOHOME"], self.slug + ".git"))

    @property
    def gitUrl(self):
        return "{0}@{1}:{2}.git".format(app.config["GIT_USER"], app.config["DOMAIN"], self.slug)

    @property
    def exists(self):
        return isdir(self.path)

    def init(self):
        if self.exists: return
        run("mkdir -p {0} && cd {0} &&  mkdir {1}.git && cd {1}.git && git init --bare".format(app.config["REPOHOME"], self.slug))

    def cloneFrom(self, url, branch = ""):
        if self.exists: return
        self.upstream = url + " " + branch
        run("mkdir -p {0} && cd {0} && git clone {2} {1}.git b {3} --bare".format(app.config["REPOHOME"], self.slug. url, branch))

    def requirePermission(self, permission):
        require_login()
        if not self.userHasPermission(get_current_user(), permission):
            abort(403)

    def clearUserPermission(self, user):
        perm = Permission.query.filter_by(user_id = user.id, repository_id = self.id).first()
        db.session.delete(perm)

    def setUserPermission(self, user, permission):
        """ `permissions` can be either of: none, find, read, write, admin """
        perm = Permission.query.filter_by(user_id = user.id, repository_id = self.id).first()

        if not perm:
            # we have no permission object, create it
            perm = Permission(user, self, permission)
            db.session.add(perm)
        else:
            # we have a permission object, edit it
            perm.access = permission

    def getUserPermission(self, user):
        p = Permission.query.filter_by(user_id = user.id, repository_id = self.id).first()
        if not p:
            return self.implicit_access if not user.is_admin else "admin"
        else:
            return p.access

    """ Users with is_admin flag have implicit admin access"""
    def userHasPermission(self, user, permission):
        p = self.getUserPermission(user)

        if permission == "admin":
            return p == "admin" or user.is_admin

        if permission == "write":
            return p in ("write", "admin")  or user.is_admin

        if permission == "read":
            return p in ("read", "write", "admin") or user.is_admin

        if permission == "find":
            return p in ("find", "read", "write", "admin") or user.is_admin

        if permission == "none":
            return not self.is_public and p == "none"

        return False

    @property
    def git(self):
        if not self._git:
            self._git = git.Repo(self.path)
        return self._git

    def findCommitContaining(self, rev, obj):
        commits = []
        for commit in git.Commit.iter_items(self.git, rev, obj.path):
            commits.append(commit)
        commits.sort(key = lambda o: o.committed_date, reverse = True)
        return commits[0]

    @property
    def commits(self):
        if not self._commits:
            self._commits = []
            for commit in git.Commit.iter_items(self.git, "master"):
                self._commits.append(commit)
        return self._commits

    @property
    def contributors(self):
        if not self._contributors:
            from minigit.filters import gitToUser
            self._contributors = []
            for commit in self.commits:
                user = gitToUser(commit.author)
                if user and not user in self._contributors:
                    self._contributors.append(user)
        return self._contributors


    def getCommit(self, rev):
        node = self.git.rev_parse(rev)

        if not node:
            return None

        if type(node) == git.Blob or type(node) == git.Tree:
            return node.commit
        if type(node) == git.Tag:
            return node.object
        if type(node) == git.Commit:
            return node

        return None
