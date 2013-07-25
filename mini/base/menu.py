from flask import url_for, request

class Menu(object):
    def __init__(self, prefix=""):
        self.items = []
        self.prefix = prefix

    def add(self, item):
        self.items.append(item)

    def add_view(self, name, title, path="", permission=None, index=0, **kwargs):
        def decorator(fun):
            endpoint = self.prefix + fun.__name__
            self.add(MenuItem(name, title, lambda: url_for(endpoint, **kwargs), path, permission, index, endpoint))
            return fun
        return decorator

class MenuItem(object):
    def __init__(self, name, title, url, path="", permission=None, index=0, endpoint=""):
        self.name = name
        self.title = title
        self._url = url
        self.path = path
        self.permission = permission
        self.index = index
        self.endpoint = endpoint
        self.children = []

    def get_url(self, *args, **kwargs):
        if callable(self._url):
            return self._url(*args, **kwargs)
        return self._url

    def has_permission(self, user):
        if self._permission is None:
            return True
        elif isinstance(self._permission, str):
            return user.has_permission(self._permission)
        elif callable(self._permission):
            return self._permission(user)
        else:
            raise Exception("Permission for menu item should be permission "
                "string or function, not %s." % type(self._permission))

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
