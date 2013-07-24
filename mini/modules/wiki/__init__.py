from mini.core import Module
from flask import render_template, abort

ext = Module("wiki", "Wiki", "miniTEAM")
app = ext.blueprint

from mini.modules.wiki.models import *
from mini.modules.wiki.views import *

ext.models = [Page, Tag]
#ext.menu.append(Menu("wiki", "Wiki", url_for("wiki.index"), ""))
#ext.menu.append(Menu("tags", "Tags", url_for("wiki.tag"), "wiki"))
