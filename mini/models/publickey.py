from mini import app, db
from mini.util import get_hooks_path
from os.path import *
from sys import argv
from datetime import datetime
import base64
from hashlib import md5

class PublicKey(db.Model):
    __tablename__ = "public_key"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(1024), unique=True)
    name = db.Column(db.String(128))
    last_access = db.Column(db.DateTime)

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

    @staticmethod
    def generate_authorized_keys_file():
        content = ""
        for key in PublicKey.query.all():
            content += "command=\"MINI_KEY_ID={key_id} {hooks_file} git-serve\" {key}\n".format(
                hooks_file=get_hooks_path(), key_id=key.id, key=key.key)

        # write authorized keys file
        with open(app.config["AUTHORIZED_KEYS"], "w") as f:
            f.write(content)

    def access(self):
        self.last_access = datetime.utcnow()
        db.session.commit()
