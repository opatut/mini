#!/usr/bin/env python2
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mini import db
import mini.modules.core.models as core
import mini.modules.wiki.models as wiki
import mini.modules.git.models as git

db.drop_all()
db.create_all()

admin = core.User()
admin.username = "admin"
admin.set_password("hunter2")
admin.permissions = """*"""
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

repo = git.Repository()
repo.slug = "testrepo"
repo.title = "Testing Repository"
repo.upstream = ""
repo.init()
db.session.add(repo)

db.session.commit()
