from mini import db

class PublicKey(db.Model):
    __tablename__ = "git_publickey"
    id = db.Column(db.Integer, primary_key = True)
    key = db.Column(db.String(1024), unique = True)
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

    guest_access = db.Column(db.Enum("none", "find", "read", "write", "admin"), default = "none")
    implicit_access = db.Column(db.Enum("none", "find", "read", "write", "admin"), default = "none")
    created = db.Column(db.DateTime)

    _git = None
    _commits = None
    _contributors = None

    def __init__(self):
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
        run("mkdir -p {0} && cd {0} && mkdir {1}.git && cd {1}.git && git init --bare".format(app.config["REPOHOME"], self.slug))

    def cloneFrom(self, url, branch = ""):
        if self.exists: return
        self.upstream = (url + " " + branch).strip()
        run("mkdir -p {0} && cd {0} && git clone {2} {1}.git --branch {3} --bare".format(app.config["REPOHOME"], self.slug, url, branch))

    @property
    def git(self):
        if not self._git:
            self._git = git.Repo(self.path)
        return self._git

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

    def get_permission(self, type="view"):
        return "git.repository.%s.%s" % (self.id, type)
