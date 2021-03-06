import subprocess, re, base64, struct, string, random
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

def hex_to_rgb_float(hex):
    if hex[0] == "#": hex = hex[1:]
    n = 2 if len(hex) == 6 else 1
    return [int(hex[i:i+n]*(3-n),16)/255.0 for i in range(0, len(hex), n)]

def random_string(length):
    return "".join(random.choice(string.ascii_letters + string.digits) for x in range(length))

def rgb_brightness(r, g, b):
    return (0.2126*r) + (0.7152*g) + (0.0722*b)

def repository_path(slug):
    from mini import app
    return abspath(join(app.config["GIT_REPOSITORY_DIRECTORY"], slug + ".git"))

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
    return abspath(join(abspath(__file__), "..", "..", "hooks.py"))

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
        return Markup(u'<span class="user anonymous"><img class="avatar" src="{0}" /> {1}</span>'.format(self.get_avatar(16), self.get_display_name()))

    def get_avatar(self, size=32):
        return "http://www.gravatar.com/avatar/{0}?s={1}&d=identicon".format(md5(self.email.lower()).hexdigest(), size)

class AccessControl(object):
    def __init__(self, current_user):
        self.current_user = current_user
        self.required_permissions = {}

    def user_has_permission(self, permission):
        return self.current_user.has_permission(permission)

    def check(self, has_permission):
        if not has_permission: raise Forbidden()

    def view_allowed(self, view):
        if not (view in self.required_permissions):
            return True
        return self.user_has_permission(self.required_permissions[view])
