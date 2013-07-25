#!/usr/bin/env python2
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mini import db
import mini.modules.core.models as core
import mini.modules.wiki.models as wiki

db.drop_all()
db.create_all()

admin = core.User()
admin.username = "admin"
admin.set_password("hunter2")
admin.permissions = """settings.core*
settings.git*
"""
print("Core Settings: ", admin.has_permission("settings.core"))
print("Wiki Settings: ", admin.has_permission("settings.wiki"))
print("Core Settings Delete: ", admin.has_permission("settings.core.delete"))
print("Login: ", admin.has_permission("login"))
db.session.add(admin)

page = wiki.Page()
page.slug = "main"
page.title = "Main Page"
page.text = "Hello World page with **markdown**."
db.session.add(page)

tag =  wiki.Tag()
tag.tag = "awesome"
tag.pages.append(page)
db.session.add(tag)

db.session.commit()
