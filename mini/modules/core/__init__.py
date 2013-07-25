from mini.base import Module
from flask import render_template, abort

ext = Module("core", "Core", "miniTEAM")
app = ext.blueprint

from models import *
from views import *

ext.models = [User]
