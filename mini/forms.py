from flask_wtf import Form
from wtforms import TextField, TextAreaField, PasswordField, ValidationError, SelectField, HiddenField
from wtforms.validators import Required, EqualTo, Email, Regexp, URL, Optional
from mini.models import User, PublicKey, Repository
from mini.models.permission import REPOSITORY_ROLES
from mini.util import hash_password, verify_key
from flask import Markup, request
import mini

class ValidLogin(object):
    def __init__(self, pw_field, message_username = "The username or password is incorrect.", message_password = "The username or password is incorrect."):
        self.pw_field = pw_field
        self.message_username = message_username
        self.message_password = message_password

    def __call__(self, form, field):
        u = User.query.filter_by(identifier=field.data).first()
        if not u:
            raise ValidationError(self.message_username)
        elif hash_password(form[self.pw_field].data) != u.password:
            raise ValidationError(self.message_password)

class ValidPublicKey(object):
    def __call__(self, form, field):
        if not verify_key(field.data.strip()):
            raise ValidationError("This is not a valid publickey.")

class UniqueObject(object):
    def __init__(self, type, column, message = "This entry already exists."):
        self.type = type
        self.column = column
        self.message = message
        self.allowed_objects = []

    def __call__(self, form, field):
        if len([x for x in self.type.query.filter_by(**{self.column:field.data.strip()}).all() if not x in self.allowed_objects]):
            raise ValidationError(self.message)


class MultiForm(Form):
    form_name = HiddenField("form name", validators=[Required()])

    def __init__(self, *args, **kwargs):
        self._form_name = type(self).__name__
        Form.__init__(self, *args, **kwargs)

    def is_submitted(self):
        return Form.is_submitted(self) and request.form.get("form_name") == self._form_name

    def hidden_tag(self, *args, **kwargs):
        self.form_name.data = self._form_name
        return Form.hidden_tag(self, *args, **kwargs)

class LoginForm(Form):
    identifier = TextField("Username or eMail", validators=[ValidLogin("password")])
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

class GeneralSettingsForm(MultiForm):
    name = TextField("Real name")
    location = TextField("Location", validators=[])
    about = TextAreaField("About", validators=[])

class ChangePasswordForm(MultiForm):
    password = PasswordField("Old password", validators=[])
    password1 = PasswordField("New password", validators=[])
    password2 = PasswordField("Repeat new password", validators=[EqualTo("password1")])

class NewEmailForm(Form):
    email = TextField("Email address", validators=[Email(), Required()])

class NewPublicKeyForm(Form):
    key = TextAreaField("SSH Public Key", validators=[
            Required(),
            ValidPublicKey(),
            UniqueObject(PublicKey, "key", "This public key is already in use.")
        ])
    name = TextField("Name for this entry", validators=[Required()])

class AddPermissionForm(Form):
    access = SelectField("Access level", choices=[(x,x) for x in REPOSITORY_ROLES])
    identifier = TextField("Username", validators=[Required()])

class EditIssueForm(MultiForm):
    title = TextField("Issue title", validators=[Required()])
    text = TextAreaField("Description")

class RequestMergeForm(MultiForm):
    title = TextField("Request title", validators=[Required()])
    text = TextAreaField("Description")
    from_rev = TextField("Merge from...")
    rev = TextField("... into", default="master")

class EditCommentForm(Form):
    text = TextAreaField("Comment", validators=[Required()])

class RepositorySettingsForm(Form):
    title = TextField("Title", validators=[Required()])
    slug = TextField("Path name", validators=[Required(),
        Regexp("^[a-z0-9A-Z_-]+$", message="Must only contain alphanumeric characters, dashes and underscores."),
        UniqueObject(Repository, "slug")])
    description = TextAreaField("Description")

    def set_repository(self, repository):
        for validator in self.slug.validators:
            if isinstance(validator, UniqueObject):
                validator.allowed_objects.append(repository)

class RepositoryCreateForm(RepositorySettingsForm):
    clone = TextField("Clone from URL", validators=[Optional(), URL()])

class TagForm(Form):
    tag = TextField("Tag", validators=[Required(), Regexp("^[\w\d_+ /-]+$", message="Invalid character.")])
    color = TextField("Color", validators=[Required(), Regexp("^([a-f0-9A-F]{3}){1,2}$", message="Invalid color code, format is #RGB or #RRGGBB.")])

class RegisterForm(Form):
    identifier = TextField("Username", validators=[Required(), UniqueObject(User, "identifier", message="This username is already in use.")])
    email = TextField("Email address", validators=[Required(), Email(), UniqueObject(mini.models.Email, "email", message="This email address is already in use.")])
    password1 = PasswordField("Password", validators=[])
    password2 = PasswordField("Password", validators=[EqualTo("password1")])
