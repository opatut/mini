
class Menu(object):
    def __init__(self, name, title, url, path="", permission=None):
        self.name = name
        self.title = title
        self._url = url
        self.path = path
        self.permission = permission

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

