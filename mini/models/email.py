from mini import db

class Email(db.Model):
    __tablename__ = "email"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True)

    user = db.relationship("User", backref="emails")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

