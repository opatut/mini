import pkgutil, os, importlib

class MiniCore(object):
    def __init__(self, app):
        self.app = app
        self.modules = {}
        self.menu_items = []

        self.load_modules()

    def load_modules(self):
        for loader, name, ispkg in pkgutil.iter_modules([os.path.abspath("mini/modules")]):
            m = importlib.import_module("mini.modules."+name)
            ext = m.ext
            self.modules[name] = ext
            self.app.register_blueprint(ext.blueprint, url_prefix='/' + ("" if name == "core" else name))
            self.menu_items += ext.menu.items
