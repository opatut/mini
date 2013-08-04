import subprocess
from hashlib import sha512, md5
from datetime import datetime
from werkzeug.exceptions import Forbidden
from flask import Markup
from flask.ext.login import login_user, logout_user, current_user

def run(p):
    child = subprocess.Popen(p, shell = True, stdout = subprocess.PIPE)

    res = ""
    while True:
        out = child.stdout.read(1024)
        if out == '' and child.poll() != None:
            break
        if out != '':
            res += out

    return res.decode("utf-8", "replace")

def get_slug(s):
    s = s.lower()
    s = re.sub(r"[\s_+]+", "-", s)
    s = re.sub("[^a-z0-9\-]", "", s)
    return s

def hash_password(s):
    return sha512((s + "TODO::secret").encode('utf-8')).hexdigest()

class AnonymousUser(object):
    def __init__(self, name="Anonymous", email="anonymous@example.com"):
        self.id = 0
        self.name = name
        self.email = email

    def has_permission(self, permission):
        return permission == "nologin"

    def get_id(self):
        return unicode(self.id)

    def is_active(self):
        return self.id != 0

    def is_anonymous(self):
        return self.id == 0

    def is_authenticated(self):
        return self.id != 0

    def logout(self):
        if self.is_anonymous(): return
        logout_user()

    def login(self):
        if self.is_anonymous(): raise Exception("Cannot login as anonymous user.")
        login_user(self)

    def get_display_name(self):
        return self.name

    def get_link(self):
        return Markup('<span class="user anonymous"><img class="avatar" src="{0}" /> {1}</span>'.format(self.get_avatar(16), self.get_display_name()))

    def get_avatar(self, size=32):
        return "http://www.gravatar.com/avatar/{0}?s={1}&d=identicon".format(md5(self.email.lower()).hexdigest(), size)

class AccessControl(object):
    def __init__(self, current_user):
        self.current_user = current_user
        self.required_permissions = {}

    def user_has_permission(self, permission):
        return self.current_user.has_permission(permission)

    def require(self, permission):
        def decorator(f):
            from functools import wraps
            @wraps(f)
            def wrapper(*args, **kwargs):
                self.check(permission)
                return f(*args, **kwargs)

            self.required_permissions[wrapper] = permission
            return wrapper
        return decorator

    def check(self, permission):
        if not self.user_has_permission(permission):
            raise Forbidden()


    def view_allowed(self, view):
        if not (view in self.required_permissions):
            return True
        return self.user_has_permission(self.required_permissions[view])
