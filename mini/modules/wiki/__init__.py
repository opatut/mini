from flask import Blueprint, render_template, abort

ext = Blueprint('wiki', __name__, template_folder='templates')

import mini.modules.wiki.models
import mini.modules.wiki.views

