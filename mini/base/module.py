from flask import Blueprint, url_for
from menu import Menu, MenuItem

class Module(object):
    def __init__(self, name, title, author):
        self.name = name
        self.blueprint = Blueprint(name, "mini.modules.%s" % name, template_folder="templates", static_folder="static")
        self.title = title
        self.author = author

        self.models = []
        self.menu = Menu(self.name + ".")

    @property
    def access(self):
        from mini import access as _a
        return _a
