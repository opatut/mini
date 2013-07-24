#!/usr/bin/env python2
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mini import db
# from mini.models import *
import mini.modules.wiki.models as wiki

db.drop_all()
db.create_all()

page = wiki.Page()
page.slug = "main"
page.title = "Main Page"
page.text = "This is some fucking retareed text ... blah I am tired don't mess with me now."
db.session.add(page)

tag =  wiki.Tag()
tag.tag = "awesome"
tag.pages.append(page)
db.session.add(tag)

db.session.commit()
