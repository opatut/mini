from flask_wtf import Form
from wtforms import TextField, PasswordField, ValidationError
from mini.models import User
from mini.util import hash_password

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
