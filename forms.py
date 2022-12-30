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


class CSRFProtection(FlaskForm):
    """ CSRF only form. """


class UserAddForm(FlaskForm):
    """Form for adding users."""

    # username: required
    username = StringField('Username', validators=[InputRequired()])
    # first_name: required
    first_name = StringField("First Name", validators=[InputRequired()])
    # last_name: required
    last_name = StringField("Last Name", validators=[InputRequired()])
    # description: larger text area, optional
    description = TextAreaField("Description", validators=[InputRequired()])
    # email: required and must be an email address
    email = EmailField('E-mail', validators=[InputRequired(), Email()])
    # password: required, and must be length >= 6
    password = PasswordField('Password', validators=[Length(min=6)])
    # image_url: can be left blank, otherwise must be a valid URL
    image_url = StringField('(Optional) Image URL')

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

