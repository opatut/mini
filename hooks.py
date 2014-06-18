#!/usr/bin/env python2
"""Receives a generic hook event, dispatching it to the mini.hooks class.

Call like this:
    python2 hooks.py <hook-name> <repository-slug> [hook-parameters]
For the hook git-serve, the repository slug is replaced with the
"""

# Setup environment
import sys, os
from os.path import *
rootpath = abspath(join(dirname(__file__)))
activate_this = join(rootpath, "env", "bin", "activate_this.py")
sys.path.insert(0, rootpath)
execfile(activate_this, dict(__file__ = activate_this))

from mini.models import *
from mini.util import *
from mini import app, db
import fileinput

# globals
key = None
user = None
repository = None

################################################################################
# HELPERS                                                                      #
################################################################################

def print_remote(msg):
    sys.stderr.write(msg + "\n")

def die(msg):
    print_remote(msg)
    sys.exit(1)

def get_repository(**kwargs):
    repository = Repository.query.filter_by(**kwargs).first()
    if not repository: die("Could not find repository.")
    return repository

def backtrack_commits(activity, commit, target):
    for ref in repository.git.refs:
        if ref.commit == commit:
            return # we had this commit already
    if commit.hexsha == target:
        return
    activity.commit_ids += commit.hexsha + ","
    for parent in commit.parents:
        backtrack_commits(activity, parent, target)

################################################################################
# HOOKS                                                                        #
################################################################################

def pre_receive():
    # revs = [line for line in sys.stdin if line.strip()]
    # print_remote("[pre-receive] The following revs are being updated")
    # for rev in revs:
    #     print_remote("  " + rev)
    # print_remote("[pre-receive] You updated %s revs." % len(revs))
    pass

def post_receive():
    revs = [line.strip() for line in sys.stdin if line.strip()]

    for line in revs:
        before, after, ref = line.split()
        branch = ref.split("/")[-1]
        if before == "0"*40: before = None
        if not before:
            activity = CreateBranchActivity()
            activity.branchname = branch
        else:
            commit = repository.get_commit(after)
            merge_only = False

            if len(commit.parents) == 2:
                # TODO: check if this was "only" a merge
                merge_only = True
                pass

            activity = PushActivity()
            activity.commit_ids = ""
            backtrack_commits(activity, commit, before)
            activity.commit_ids.strip(",")
        activity.repository = repository
        activity.user = user
        db.session.add(activity)
        db.session.commit()



def git_serve():
    command = os.getenv("SSH_ORIGINAL_COMMAND")

    # split the command
    action, repo = command.split()

    # check action
    if not action in ("git-receive-pack", "git-upload-pack"):
        die("Authenticated as %s. This remote user is only for use with git." % user.username)
    permission = {"git-receive-pack": "write", "git-upload-pack": "read"}[action]

    # cut away quotation marks
    if (repo[0] == "'" and repo[-1] == "'") or (repo[0] == '"' and repo[-1] == '"'):
        repo = repo[1:-1]

    # cut away the ".git" fake-extension
    if repo[-4:] == ".git":
        repo = repo[:-4]

    repository = get_repository(slug=repo)

    if not repository.has_permission(user, permission):
        die("Permission denied - no " + permission + " access.")

    key.access()
    print_remote("User " + user.username + " authorized for " + permission + " access.")
    os.system("cd {0} && git shell -c {1}".format(app.config["GIT_REPOSITORY_DIRECTORY"], shellquote(command)))


################################################################################
# MAIN                                                                         #
################################################################################

if __name__ == "__main__":
    if len(sys.argv) < 2:
        die("Not enough arguments.")

    hook = sys.argv[1]

    if hook != "git-serve" and len(sys.argv) < 3:
        die("Not enough arguments.")

    # retrieve key
    key_id = os.getenv("MINI_KEY_ID")
    key = PublicKey.query.filter_by(id=key_id).first()

    # if not key: die("Unable to associate SSH Key. Please add it to your profile.")
    # user = key.user
    user = User.query.filter_by(username="peter").first()


    if hook != "git-serve": # git-serve finds its own repository
        repository = get_repository(slug=sys.argv[2])

    args = sys.argv[3:]

    if hook == "git-serve":
        git_serve()
    elif hook == "pre-receive":
        pre_receive(*args)
    elif hook == "post-receive":
        post_receive(*args)
    else:
        die("Invalid hook executed in server: " + hook + ".")
