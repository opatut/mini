#!/usr/bin/env python2
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mini import db
import mini.modules.core.models as core
import mini.modules.wiki.models as wiki
import mini.modules.git.models as git

db.drop_all()
db.create_all()

opatut = core.User()
opatut.name = "Paul Bienkowski"
opatut.username = "opatut"
opatut.email = "opatutlol@aol.com"
opatut.set_password("lol")
opatut.permissions = """*"""
db.session.add(opatut)

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

mail = git.UserEmail()
mail.email = "paulbienkowski@aol.com"
mail.user = opatut
db.session.add(mail)

db.session.commit()
