from mini import db
from mini import app as main_app
from mini.base import Module
from flask import render_template, abort

ext = Module("git", "Git", "miniTEAM")
app = ext.blueprint

from models import *
from views import *
from filters import *

ext.models = [PublicKey, Repository]

