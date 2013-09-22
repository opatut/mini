#!/usr/bin/env python2
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mini import db
from mini.models import *

db.drop_all()
db.create_all()

opatut = User()
opatut.name = "Paul Bienkowski"
opatut.username = "opatut"
opatut.email = "opatutlol@aol.com"
opatut.set_password("lol")
opatut.permissions = """*"""
db.session.add(opatut)

page = WikiPage()
page.slug = "main"
page.title = "Main Page"
page.text = "Hello World page with **markdown**."
db.session.add(page)

repo = Repository()
repo.slug = "testrepo"
repo.title = "Testing Repository"
repo.upstream = ""
repo.init()
db.session.add(repo)

mail = Email()
mail.email = "paulbienkowski@aol.com"
mail.user = opatut
db.session.add(mail)

issuetag1 = IssueTag()
issuetag1.tag = "frontend"
issuetag1.color = "FFAA55"
repo.issue_tags.append(issuetag1)
db.session.add(issuetag1)

issuetag2 = IssueTag()
issuetag2.tag = "backend"
issuetag2.color = "5588FF"
repo.issue_tags.append(issuetag2)
db.session.add(issuetag2)

issue = Issue()
issue.number = repo.next_issue_number
repo.next_issue_number += 1
issue.title = "Test Issue"
issue.text = "Just testing, *nevermind*!"
issue.status = "open"
issue.issue_tags.append(issuetag1)
issue.issue_tags.append(issuetag2)
issue.assignee = opatut
issue.repository = repo
db.session.add(issue)

issue = Issue()
issue.number = repo.next_issue_number
repo.next_issue_number += 1
issue.title = "Idea for implementation"
issue.text = "Just testing more, *nevermind*!"
issue.status = "discussion"
issue.repository = repo
issue.issue_tags.append(issuetag1)
db.session.add(issue)


db.session.commit()
