from flask import Blueprint, url_for
from menu import Menu

class Module(object):
    def __init__(self, name, title, author):
        self.name = name
        self.blueprint = Blueprint(name, "mini.modules.%s" % name, template_folder="templates")
        self.title = title
        self.author = author

        self.models = []
        self.menu = []

    def add_menu(self, name, title, path="", permission=None):
        def decorator(fun):
            self.menu.append(Menu(name, title, lambda: url_for("%s.%s" % (self.name, fun.__name__)), path, permission))
            return fun
        return decorator
