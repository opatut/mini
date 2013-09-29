#!/usr/bin/env python2
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mini import app, db
from mini.models import User, Email

db.drop_all()
db.create_all()

admin = User()
admin.name = "Administrator"
admin.username = "admin"
admin.set_password("admin")
admin.permissions = """*"""
db.session.add(admin)

mail = Email()
mail.email = "admin@" + app.config["DOMAIN"]
mail.is_default = True
mail.is_gravatar = True
mail.user = admin
db.session.add(mail)

db.session.commit()

print("Created user 'admin' with password 'admin'.")
