#!/usr/bin/env python2
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mini import db
from mini.models import *
from datetime import timedelta

db.drop_all()
db.create_all()

tester = User()
tester.name = "Peter Langbein"
tester.username = "peter"
tester.set_password("lol")
db.session.add(tester)

mail = Email()
mail.email = "test@example.com"
mail.is_gravatar = True
mail.is_default = True
mail.user = tester
db.session.add(mail)

opatut = User()
opatut.name = "Paul Bienkowski"
opatut.username = "opatut"
opatut.set_password("lol")
opatut.permissions = """*"""
db.session.add(opatut)

key = PublicKey()
key.user = opatut
key.key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDRUFLcksSX57IC7Z1yGWWYignX7tnn0c2EffImrZbUoZTtxpQPvsnkw191/NAb9ol8K0ndjLYtaaRIxYsXwAcLaT+/Cu0K+Jd7E+CKa1KzJJNhYsnEJIYH+JMFbBcq3IP+r5XI5E35SA0mjWlPHmqFDssotSPd9f0Q66OIy7MNscrJaNNUSauVkNVr/SlMpEHB0mpY0fZJZz0Qlqb2PV7OWvh332bMdM70+dl9CyxNRNruApq95gI+IUYac7gMqgtoFIsxojBvaETuMqqhcfwuc9wx++ezxqq2UgMV9KDGlv9rfrjPr+P3/ZhUD0afo75BalCLyEAVeYugCv8hRg+lD1IgT7oJy1WVPIKAHgM8KjqDKWUDBJRdnBokMQ/y8PEaGRBzpWk5YIWefDf901xosgi4L+DMr2fxb7wRJOLb88Y+MmBuaN5ODa6FGMo7Ql7xRwgbVleS+J46mr2HG7ITTSLvn5on7K3cAfvUQsFfcesYLoHGbL6Lf7VY7HxAEMxrj9QJyp3LWrHw7kTdxGsT34ZQCcbI4NM0h++LVer5yjlMgOM8yf5ehc6hMIj2s417HNBKWMeojyZG3ThvtmQmhvxVyrWdFhntNB0tB0RxMiINQEBHLV6S/OHg9TKEhcPn1csG8H2QjXf1k88cGjuFu6xzCam+0Hfk/2DDZmkRVQ== paul@newton"
key.name = "newton/curry"
db.session.add(key)

repo = Repository()
repo.slug = "testrepo"
repo.title = "Testing Repository"
repo.upstream = ""
repo.description = """This is a repository that was just created for testing the webapp
and is not intended to be used whatsoever. It may contain a lot of useless commits
and files, use at your own risk."""
repo.init()
db.session.add(repo)

mail = Email()
mail.email = "paulbienkowski@aol.com"
mail.is_default = True
mail.user = opatut
db.session.add(mail)

mail = Email()
mail.email = "opatutlol@aol.com"
mail.is_gravatar = True
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

a5 = CreateIssueActivity()
a5.repository = repo
a5.user = opatut
a5.issues.append(issue)

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

a8 = ModifyIssueActivity()
a8.repository = repo
a8.user = opatut
a8.issue = issue
a8.new_status = "closed"
issue.status = "closed"
a8.new_assignee = None

a6 = CreateIssueActivity()
a6.repository = repo
a6.user = opatut
a6.issues.append(issue)

comment = IssueComment()
comment.author = opatut
comment.text = "I said [something](http://google.de)."
issue.issue_comments.append(comment)
db.session.add(comment)

a7 = CreateIssueActivity()
a7.repository = repo
a7.user = opatut

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
    a7.issues.append(issue)


merge1 = Merge()
merge1.number = repo.next_issue_number
repo.next_issue_number += 1
merge1.title = "Please merge me"
merge1.text = "Just testing, *nevermind*!"
merge1.status = "open"
merge1.author = opatut
merge1.from_repository = repo
merge1.from_rev = "30785629a6"
merge1.repository = repo
merge1.rev = "master"
db.session.add(merge1)

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

## ACTIVITIES ##

# a1 = PushActivity()
# a1.user = opatut
# a1.repository = repo
# a1.commit_ids = "30785629a6,d1ca43bd60,76ae3390b9"

# a2 = PushActivity()
# a2.user = opatut
# a2.repository = repo
# a2.commit_ids = "29231e6092"
# a2.date -= timedelta(hours=5, minutes=24)

a3 = CommentActivity()
a3.user = opatut
a3.repository = repo
a3.issuecomment = comment
a3.date -= timedelta(hours=3, minutes=12)

a4 = CreateBranchActivity()
a4.user = opatut
a4.repository = repo
a4.branchname = "feature"
a4.date -= timedelta(days=2)

db.session.commit()

PublicKey.generate_authorized_keys_file()
repo.install_all_hooks()
