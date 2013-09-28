import subprocess, re, base64
from hashlib import sha512, md5
from datetime import datetime
from werkzeug.exceptions import Forbidden
from flask import Markup
from flask.ext.login import login_user, logout_user, current_user
from os.path import *

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

def validate_slug(obj):
    objs = type(obj).query.filter_by(slug=obj.slug).all()
    return len(objs) == 0 or (len(objs) == 1 and objs[0] == obj)

def generate_new_slug(obj):
    old_slug = obj.slug
    obj.slug = get_slug(obj.title)
    if validate_slug(obj):
        return True
    else:
        obj.slug = old_slug
        return False

def get_hooks_path():
    return abspath(join(basename(__file__), "..", "hooks.py"))

def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"

def hash_password(s):
    return sha512((s + "TODO::secret").encode('utf-8')).hexdigest()

def verify_key(key):
    try:
        type, key_string, comment = key.strip().split()
        data = base64.decodestring(key_string)
        int_len = 4
        str_len = struct.unpack('>I', data[:int_len])[0] # this should return the length of the type
        return data[int_len:int_len + str_len] == type
    except:
        return False


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
            print("Decorating function %s for permission %s" % (f, permission))
            from functools import wraps
            @wraps(f)
            def wrapper(*args, **kwargs):
                print("Wrapped function %s for permission %s" % (f, permission))
                self.check(permission)
                return f(*args, **kwargs)

            self.required_permissions[wrapper] = permission
            return wrapper
        return decorator

    def check(self, has_permission):
        if not has_permission: raise Forbidden()

    def view_allowed(self, view):
        if not (view in self.required_permissions):
            return True
        return self.user_has_permission(self.required_permissions[view])
