from flask_wtf import Form
from wtforms import TextField, TextAreaField, PasswordField, ValidationError, SelectField
from wtforms.validators import Required
from mini.models import User
from mini.util import hash_password
from flask import Markup

class ValidLogin(object):
    def __init__(self, pw_field, message_username = "The username or password is incorrect.", message_password = "The username or password is incorrect."):
        self.pw_field = pw_field
        self.message_username = message_username
        self.message_password = message_password

    def __call__(self, form, field):
        u = User.query.filter_by(username=field.data).first()
        if not u:
            raise ValidationError(self.message_username)
        elif hash_password(form[self.pw_field].data) != u.password:
            raise ValidationError(self.message_password)

class LoginForm(Form):
    username = TextField("Username or eMail", validators=[ValidLogin("password")])
    password = PasswordField("Password", validators=[])

class WikiPageForm(Form):
    title = TextField("Page title", validators=[Required()])
    parent_page_id = SelectField("Parent page", choices=[], coerce=int)
    text = TextAreaField("Content", validators=[Required()])

    def init_parent(self, page):
        self.parent_page_id.choices = []

        def add_choices(pages, depth = 0):
            for p in pages:
                if p == page: continue
                self.parent_page_id.choices.append((p.id, depth * "~ " + p.title))
                add_choices(p.child_pages, depth+1)

        self.parent_page_id.choices.append((0, "- none -"))
        add_choices(page.repository.get_root_wiki_pages())
        if page.parent_page: self.parent_page_id.default = page.parent_page.id
