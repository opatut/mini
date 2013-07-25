from mini.base import Module
from flask import render_template, abort

ext = Module("wiki", "Wiki", "miniTEAM")
app = ext.blueprint

from models import *
from views import *

ext.models = [Page, Tag]

@app.context_processor
def inject():
    return dict(wiki_tags=Tag.query.all())
