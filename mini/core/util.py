import re, os, sys, subprocess, iso8601, pytz, base64, struct
from hashlib import sha512, md5
from mini import app
from os.path import *
from flask import abort
from datetime import datetime

def run(p):
    if app.debug: print("$ " + p)

    child = subprocess.Popen(p, shell = True, stdout = subprocess.PIPE)

    res = ""
    while True:
        out = child.stdout.read(1024)
        if out == '' and child.poll() != None:
            break
        if out != '':
            res += out

    return res.decode("utf-8", "replace")

def get_slug(s):
    s = s.lower()
    s = re.sub(r"[\s_+]+", "-", s)
    s = re.sub("[^a-z0-9\-]", "", s)
    return s

def get_email_user(email):
    if not email: return None
    from minigit.models import Email
    m = Email.query.filter_by(address = email).first()
    if not m: return None
    return m.user

def parse_date(s):
    # Parse timezone offset
    stamp, tz = s.split()
    timezone = iso8601.iso8601.parse_timezone(tz[:3] + ':' + tz[3:])
    return datetime.fromtimestamp(int(stamp), timezone).astimezone(pytz.utc).replace(tzinfo = None)

def hash_password(s):
    return sha512((s + app.config['SECRET_KEY']).encode('utf-8')).hexdigest()

def write(l):
    sys.stderr.write(l + "\n")

def die(message):
    write(message)
    log_access("DENIED - " + message)
    sys.exit(1)

def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"

