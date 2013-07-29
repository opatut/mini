from flask import url_for, request

class Menu(object):
    def __init__(self, prefix=""):
        self.items = []
        self.prefix = prefix

    def add(self, item):
        self.items.append(item)

    def add_view(self, name, title, path="", index=0, **kwargs):
        def decorator(fun):
            endpoint = self.prefix + fun.__name__
            self.add(MenuItem(name, title, lambda: url_for(endpoint, **kwargs), path, index, endpoint, fun))
            return fun
        return decorator

class MenuItem(object):
    def __init__(self, name, title, url, path="", index=0, endpoint="", view_function=None):
        self.name = name
        self.title = title
        self._url = url
        self.path = path
        self.index = index
        self.endpoint = endpoint
        self.view_function = view_function
        self.children = []

    def get_url(self, *args, **kwargs):
        if callable(self._url):
            return self._url(*args, **kwargs)
        return self._url

    def is_shown(self):
        from mini import access
        return access.view_allowed(self.view_function)

    def __repr__(self):
        return '<Menu "%s">'%self.name

    def is_current(self):
        return self.endpoint == request.endpoint

    def find_current(self):
        if self.is_current():
            return self

        for child in self.children:
            current = child.find_current()
            if current:
                return current
        return None
