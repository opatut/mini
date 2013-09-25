from mini import app, db
from mini.util import run, get_hooks_path
from mini.models.user import User
from mini.models.permission import Permission
from datetime import datetime
from os.path import abspath, join, isdir
from flask.ext.login import current_user
import git, os

class Repository(db.Model):
    __tablename__ = "repository"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(64), unique=True, default="")
    title = db.Column(db.String(128), default="")
    upstream = db.Column(db.String(256)) # URL BRANCH
    created = db.Column(db.DateTime)
    next_issue_number = db.Column(db.Integer, default=1)

    _git = None
    _commits = None
    _contributors = None

    def __init__(self):
        self.created = datetime.utcnow()
        self.next_issue_number = 1

    @property
    def path(self):
        return abspath(join(app.config["GIT_REPOSITORY_DIRECTORY"], self.slug + ".git"))

    @property
    def git_url(self):
        return "{0}@{1}:{2}.git".format(app.config["GIT_USER"], app.config["DOMAIN"], self.slug)

    @property
    def exists(self):
        return isdir(self.path)

    def init(self):
        if self.exists: return
        self._git = git.Repo.init(self.path, bare=True)

    def clone_from(self, url, branch = ""):
        if self.exists: return
        self.upstream = (url + " " + branch).strip()
        self._git = git.Repo.clone_from(self.upstream, self.path, bare=True)

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

    @property
    def implicit_permission(self):
        permission = Permission.query.filter_by(repository=self, user=None).first()
        if not permission:
            permission = Permission(None, self, "none")
            db.session.add(permission)
            db.session.commit()
        return permission

    def get_explicit_permission(self, user):
        if not user: return self.implicit_permission
        return Permission.query.filter_by(repository_id=self.id, user_id=user.id).first()

    def set_permission(self, user, access):
        if user == current_user: return False # never allow this

        permission = self.get_explicit_permission(user)

        if not permission:
            permission = Permission(user, self, access)
            db.session.add(permission)
        else:
            permission.access = access

        db.session.commit()
        return True

    def has_permission(self, user, access):
        return user.has_permission("repositories.all.%s" % access) or \
            (self.get_explicit_permission(user) or self.implicit_permission).satisfies(access)

    def get_users_with_permission(self, access):
        return [user for user in User.query.all() if self.has_permission(user, access)]

    def get_root_wiki_pages(self):
        return [page for page in self.wiki_pages if not page.parent_page]

    def get_hook_file(self, hook):
        return abspath(join(self.path, "hooks", hook))

    def install_hook(self, hook):
        content = "#!/bin/bash\npython2 {hooks_file} {hook} {slug} \"$@\"".format(
            hooks_file=get_hooks_path(), hook=hook, slug=self.slug)

        path = self.get_hook_file(hook)
        with open(path, "w") as f:
            f.write(content)
            f.close()
            os.chmod(path, 0755) # set executable

    def uninstall_hook(self, hook):
        os.remove(self.get_hook_file(hook))

    def install_all_hooks(self):
        for hook in ["pre-receive", "post-receive"]:
            self.install_hook(hook)
