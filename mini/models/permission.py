from mini import db

# Used to map user<->repository permissions
# For the

REPOSITORY_ROLES = ["none", "find", "read", "comment", "write", "mod", "admin"]

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    access = db.Column(db.Enum(*REPOSITORY_ROLES), default = "none")

    user = db.relationship("User", backref="repository_permissions")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    repository = db.relationship("Repository", backref="permissions")
    repository_id = db.Column(db.Integer, db.ForeignKey("repository.id"))

    def __init__(self, user, repository, access):
        self.user = user
        self.repository = repository
        self.access = access

    def satisfies(self, access):
        return access in REPOSITORY_ROLES and REPOSITORY_ROLES.index(self.access) >= REPOSITORY_ROLES.index(access)
