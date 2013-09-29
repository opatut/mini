from mini import app, db, mail
from flask.ext.sendmail import Message
from mini.models import *
from flask import render_template, g

def get_sender(mode="default"):
    senders = app.config["MAIL_SENDERS"]
    if mode in senders: return senders[mode]
    else: return senders["default"]

def send(msg):
    if app.config["TESTING"] or app.config["MAIL_SUPPRESS_SEND"]:
        print("="*79)
        print("Subject:" + msg.subject)
        print("To:     " + str(msg.recipients))
        print("Content:" + msg.body)
        print("="*79)
        g.outbox = [msg]
    else:
        mail.send(msg)

def registration(user):
    msg = Message("Registration at %s" % app.config["DOMAIN"], sender=get_sender())
    msg.add_recipient(user.default_email.email)
    msg.body = render_template("mails/registration.txt", user=user)
    send(msg)
