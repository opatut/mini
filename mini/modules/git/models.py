from mini import app as main_app
from mini.modules.git import app, ext, db
from mini.base.util import run
from datetime import datetime
from os.path import abspath, join, isdir
#import git
from git import Repo

class UserEmail(db.Model):
    __tablename__ = "git_user_email"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True)

    user = db.relationship("User", backref="user_emails")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class PublicKey(db.Model):
    __tablename__ = "git_publickey"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(1024), unique=True)
    name = db.Column(db.String(128))

    user = db.relationship("User", backref="public_keys")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def set_key(self, key):
        self.key = key.strip()

    @property
    def fingerprint(self):
        key = base64.b64decode(self.key.strip().split(None, 2)[1])
        fp_plain = md5(key).hexdigest()
        return ':'.join(a+b for a,b in zip(fp_plain[::2], fp_plain[1::2]))

    @property
    def type(self):
        try:
            type, other = key.strip().split(None, 1)
            return type
        except:
            return None

class Repository(db.Model):
    __tablename__ = "git_repository"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(64), unique=True, default="")
    title = db.Column(db.String(128), default="")
    upstream = db.Column(db.String(256)) # URL BRANCH
    created = db.Column(db.DateTime)

    _git = None
    _commits = None
    _contributors = None

    def __init__(self):
        self.created = datetime.utcnow()

    @property
    def path(self):
        return abspath(join(main_app.config["GIT_REPOSITORY_DIRECTORY"], self.slug + ".git"))

    @property
    def git_url(self):
        return "{0}@{1}:{2}.git".format(main_app.config["GIT_USER"], main_app.config["DOMAIN"], self.slug)

    @property
    def exists(self):
        return isdir(self.path)

    def init(self):
        if self.exists: return
        self._git = Repo.init(self.path, bare=True)

    def clone_from(self, url, branch = ""):
        if self.exists: return
        self.upstream = (url + " " + branch).strip()
        self._git = Repo.clone_from(self.upstream, self.path, bare=True)

    @property
    def git(self):
        if not self._git:
            self._git = git.Repo(self.path)
        return self._git

    def get_commits(self):
        if not self._commits:
            self._commits = []
            for head in self.git.heads:
                for commit in git.Commit.iter_items(self.git, head):
                    if not commit in self._commits:
                        self._commits.append(commit)
            self._commits.sort(key=lambda c: c.committed_date)
        return self._commits

    def get_commit(self, rev):
        node = self.git.rev_parse(rev)

        if type(node) == git.Blob or type(node) == git.Tree:
            return node.commit
        elif type(node) == git.Tag:
            return node.object
        elif type(node) == git.Commit:
            return node
        else:
            return None

    # find, read, write, admin
    def get_permission(self, type):
        return "git.repository.%s.%s" % (self.id, type)
