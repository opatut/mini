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
issue.author = opatut
issue.repository = repo
db.session.add(issue)

issue = Issue()
issue.number = repo.next_issue_number
repo.next_issue_number += 1
issue.title = "Idea for implementation"
issue.text = "Just testing more, *nevermind*!"
issue.status = "discussion"
issue.repository = repo
issue.author = opatut
issue.issue_tags.append(issuetag1)
db.session.add(issue)

comment = IssueComment()
comment.author = opatut
comment.text = "I said [something](http://google.de)."
issue.issue_comments.append(comment)
db.session.add(comment)

for s in ("open", "discussion", "closed", "wip", "invalid"):
    issue = Issue()
    issue.number = repo.next_issue_number
    repo.next_issue_number += 1
    issue.title = "Status " + s + " test"
    issue.text = "Just testing more, *nevermind*!"
    issue.status = s
    issue.repository = repo
    issue.author = opatut
    db.session.add(issue)

wiki_main = WikiPage()
wiki_main.slug = "main"
wiki_main.title = "Main Page"
wiki_main.text = """#Main Page

This is the main wiki page of some repository. It is awesome.
"""
wiki_main.repository = repo
db.session.add(wiki_main)

wiki_sub = WikiPage()
wiki_sub.slug = "subpage-in-wiki"
wiki_sub.title = "Subpage in wiki"
wiki_sub.text = """#Subpage

This is some sort of subpage.
"""
wiki_sub.repository = repo
wiki_sub.parent_page = wiki_main
db.session.add(wiki_sub)

db.session.commit()
