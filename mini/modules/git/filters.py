from mini import app
from mini.base.util import AnonymousUser
from mini.modules.core.models import User
from mini.modules.git.models import UserEmail
from datetime import datetime as dt, date as d
from flask import Markup
import time, os, pygments, pygments.lexers, pygments.formatters, git, re
from os.path import *

# UTILITY to wrap a date/time in a span tag with a title
def date_title(s, fmt, with_title=True):
    if with_title: return Markup("<span title=\"%s UTC\">%s</span>" % (datetime(s, False), fmt))
    return fmt

# shorten a hexsha
@app.template_filter()
def shortsha(s):
    return s[:10]

# shorten a string
@app.template_filter()
def shorten(s, length):
    return s[:length] + ("..." if len(s) > length else "")

# shorten a string
@app.template_filter()
def first_line(s):
    return s.splitlines()[0]

@app.template_filter()
def splitlines(s):
    return s.splitlines()

@app.template_filter()
def parentpath(s):
    return normpath(join(s, ".."))

@app.template_filter()
def filesize(s):
    s = int(s)
    for x in ['B', 'KB','MB','GB','TB']:
        if s < 1024.0:
            return "%3.f %s" % (s, x)
        s /= 1024.0


# convert unix timestamp to datetime
@app.template_filter()
def git_committer_time(commit):
    return dt.fromtimestamp(commit.committed_date + commit.committer_tz_offset)

# find a user
@app.template_filter()
def git_user(u):
    user = User.query.filter_by(email=u.email).first()
    if not user:
        mail = UserEmail.query.filter_by(email=u.email).first()
        if not mail: return AnonymousUser(u.name, u.email)
        user = mail.user
    return user

# format a timestamp in default time format (00:00:00)
@app.template_filter()
def time(s, with_title=True):
    return date_title(s, s.strftime("%H:%M:%S"), with_title)

# format a timestamp in default date format (0000-00-00)
@app.template_filter()
def date(s, with_title=True):
    return date_title(s, s.strftime("%Y-%m-%d"), with_title)

# format a timestamp in default format (0000-00-00 00:00:00)
@app.template_filter()
def datetime(s, with_title=True):
    return date_title(s, s.strftime("%Y-%m-%d %H:%M:%S"), with_title)

# format a timestamp as human readable date
@app.template_filter()
def date_human(s, with_title=True):
    return date_title(s, "Today" if d.today() == s.date() else s.strftime("%B %d, %Y"), with_title)

@app.template_filter()
def filetype(blob):
    if type(blob) == git.Tree:
        return "folder"

    if blob.size == 0:
        return "empty-file"

    ext = extension(blob)
    mimetype = blob.mime_type

    IMAGE_TYPES = ("png", "jpg", "jpeg", "tga", "gif", "bmp")

    if ext in IMAGE_TYPES:
        return "image"

    if mimetype.split("/")[0] == "text":
        return "textfile"

    return "file"

@app.template_filter()
def extension(file):
    return splitext(file.name)[1][1:].lower()

@app.template_filter()
def pathsplit(pathstr, maxsplit=None):
    """split relative path into list"""
    path = [pathstr]
    while True:
        oldpath = path[:]
        path[:1] = list(os.path.split(path[0]))
        if path[0] == '':
            path = path[1:]
        elif path[1] == '':
            path = path[:1] + path[2:]
        if path == oldpath:
            return path
        if maxsplit is not None and len(path) > maxsplit:
            return path

@app.template_filter()
def highlightsheet(s):
    return pygments.formatters.HtmlFormatter(style = s).get_style_defs('.highlight')

@app.template_filter()
def highlight(s, filename):
    s = s.strip()
    try:
        lexer = pygments.lexers.get_lexer_for_filename(filename)
    except pygments.util.ClassNotFound:
        lexer = pygments.lexers.TextLexer()
    formatter = pygments.formatters.HtmlFormatter(linenos = True)
    return Markup(pygments.highlight(s, lexer, formatter))


@app.template_filter()
def find_readme(tree):
    for x in tree.blobs:
        if x.name.upper().startswith("README"):
            return x

@app.template_filter()
def diffLineType(line):
    if line[:3] == "---":
        return "from"
    elif line[:3] == "+++":
        return "to"
    elif line[:2] == "@@":
        return "section"
    elif line[:1] == "-":
        return "deletion"
    elif line[:1] == "+":
        return "insertion"
    return "context"

@app.template_filter()
def diffParseSection(line):
    m = re.search('^@@\s*-([0-9]+),[0-9]+\s+\+([0-9]+),[0-9]+\s*@@.*$', line)
    return (int(m.group(1)), int(m.group(2)))

