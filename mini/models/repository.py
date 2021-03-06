from mini import app, db, cache
from mini.util import run, get_hooks_path, repository_path
from mini.network import Network
from mini.models.user import User
from mini.models.permission import Permission
from datetime import datetime, timedelta
from os.path import abspath, join, isdir
from flask import flash, Markup, url_for
from flask.ext.login import current_user
import git, os, shutil

class Repository(db.Model):
    __tablename__ = "repository"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(64), unique=True, default="")
    title = db.Column(db.String(128), default="")
    description = db.Column(db.Text)
    upstream = db.Column(db.String(256)) # URL BRANCH
    created = db.Column(db.DateTime)
    next_issue_number = db.Column(db.Integer, default=1)

    issues = db.relationship("Issue", backref="repository", lazy="dynamic")
    activities = db.relationship("Activity", backref="repository", lazy="dynamic")

    _git = None
    _commits = None
    _contributors = None
    _network = None

    def __init__(self):
        self.created = datetime.utcnow()
        self.next_issue_number = 1

    @property
    def path(self):
        return repository_path(self.slug)

    @property
    def git_url(self):
        return "{0}@{1}:{2}.git".format(app.config["GIT_USER"], app.config["DOMAIN"], self.slug)

    @property
    def exists(self):
        return isdir(self.path)

    def init(self):
        if self.exists: return
        try:
            self._git = git.Repo.init(self.path, bare=True)
            return True
        except git.GitCommandError, e:
            return False

    def clone_from(self, url, branch = ""):
        if self.exists: return
        self.upstream = (url + " " + branch).strip()
        try:
            self._git = git.Repo.clone_from(self.upstream, self.path, bare=True)
            return True
        except git.GitCommandError, e:
            return False

    @property
    def git(self):
        if not self._git:
            self._git = git.Repo(self.path, odbt=git.GitCmdObjectDB)
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
        if not rev: return None
        node = self.git.rev_parse(rev)

        if type(node) == git.Blob or type(node) == git.Tree:
            return node.commit
        elif type(node) == git.Tag:
            return node.object
        elif type(node) == git.Commit:
            return node
        else:
            return None

    def get_commit_activity(self, normalize=False):
        weeks = {}
        for commit in self.git.iter_commits('master'):
            date = datetime.fromtimestamp(commit.committed_date + commit.committer_tz_offset).date()
            week = date - timedelta(days=date.weekday())
            stats = commit.stats
            if not week in weeks:
                weeks[week] = dict(deletions=0, insertions=0, lines=0, commits=0)
            weeks[week]["deletions"] += stats.total["deletions"]
            weeks[week]["insertions"] += stats.total["insertions"]
            weeks[week]["lines"] += stats.total["lines"]
            weeks[week]["commits"] += 1
        if normalize:
            start = min(weeks.keys())
            end = max(weeks.keys())
            while start < end:
                if not start in weeks:
                    weeks[start] = dict(deletions=0, insertions=0, lines=0, commits=0)
                start += timedelta(days=7)
        return weeks

    def get_contributions(self, threshold=0.01):
        from mini.filters import git_user
        data = {}
        for commit in self.git.iter_commits('master'):
            user = git_user(commit.author).name
            if not user in data: 
                data[user] = dict(lines=0, deletions=0, insertions=0, commits=0)
            data[user]["deletions"] += commit.stats.total["deletions"]
            data[user]["insertions"] += commit.stats.total["insertions"]
            data[user]["lines"] += commit.stats.total["lines"]
            data[user]["commits"] += 1

        if threshold:
            minimum = sum([stats["commits"] for stats in data.itervalues()]) * threshold
            out = dict(lines=0, deletions=0, insertions=0, commits=0)
            for user, stats in data.items():
                if stats["commits"] < minimum:
                    out["deletions"]  += stats["deletions"]
                    out["insertions"] += stats["insertions"]
                    out["lines"]      += stats["lines"]
                    out["commits"]    += stats["commits"]
                    del data[user]
            if out["commits"]:
                data["others"] = out

        return data

    def is_branch(self, name):
        return len([x for x in self.git.branches if x.name==name or x.path==name])>0

    def find_commit_containing(self, rev, file):
        commits = []
        for commit in git.Commit.iter_items(self.git, rev, file.path):
            commits.append(commit)
        commits.sort(key = lambda o: o.committed_date, reverse = True)
        return commits[0]

    @property
    def implicit_permission(self):
        permission = Permission.query.filter_by(repository=self, member=None).first()
        if not permission:
            permission = Permission(None, self, "none")
            db.session.add(permission)
            db.session.commit()
        return permission

    def get_explicit_permission(self, member):
        if not member: return self.implicit_permission
        return Permission.query.filter_by(repository_id=self.id, member_id=member.id).first()

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

    def move_to(self, slug):
        shutil.move(self.path, repository_path(slug))
        self.slug = slug

    def get_link(self, size=16):
        return Markup('<span class="repository"><a href="{0}">{1}</a></span>'.format(self.get_url(), self.title))

    def get_url(self):
        return url_for("repository", slug=self.slug)

    def clear_cache(self):
        # stats caches
        for type in ["contributions", "commit-activity", "network"]:
            cache.delete_memoized('api_stats', self.slug, type)

    def get_network(self):
        if not self._network:
            self._network = Network(self)
            self._network.generate()
        return self._network