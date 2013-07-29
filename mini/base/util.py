import subprocess
from hashlib import sha512, md5
from datetime import datetime
from werkzeug.exceptions import Forbidden

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

    def logout(self):
        pass

    def login(self):
        raise Exception("Cannot login as anonymous user.")

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
