from mini import db

class PublicKey(db.Model):
    __tablename__ = "public_key"
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

