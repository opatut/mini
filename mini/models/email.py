from mini import db
from hashlib import md5

class Email(db.Model):
    __tablename__ = "email"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True)
    is_default = db.Column(db.Boolean, default=False)
    is_gravatar = db.Column(db.Boolean, default=False)

    user = db.relationship("User", backref="emails")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def get_avatar(self, size = 32):
        return "http://www.gravatar.com/avatar/{0}?s={1}&d=identicon".format(md5(self.email.lower()).hexdigest(), size)

