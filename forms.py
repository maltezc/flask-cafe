"""Forms for Flask Cafe."""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, SelectField, EmailField, PasswordField
from wtforms.validators import InputRequired, DataRequired, Email, Length

class CafeAddUpdateForm(FlaskForm):
    """Form for adding users."""

    name = StringField('Name', validators=[InputRequired()])
    description = TextAreaField('Description')
    url = URLField('(Optional) URL')
    address = StringField('Address', validators=[InputRequired()])
    city_code = SelectField("City Code", coerce=str) # TODO: set this up to be dynamic and pull from DB
    image_url = URLField('(Optional) Image URL')


class CSRFOnlyForm(FlaskForm):
    """ CSRF only form. """


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[InputRequired()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    description = TextAreaField("Description", validators=[InputRequired()])
    email = EmailField('E-mail', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    image_url = StringField('(Optional) Image URL')

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class ProfileEditForm(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    description = TextAreaField("Description", validators=[InputRequired()])
    email = EmailField('E-mail', validators=[InputRequired(), Email()])
    image_url = StringField('(Optional) Image URL')

