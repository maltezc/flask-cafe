"""Forms for Flask Cafe."""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, SelectField
from wtforms.validators import InputRequired

class CafeAddUpdateForm(FlaskForm):
    """Form for adding users."""

    # name: required
    name = StringField('Name', validators=[InputRequired()])
    # description: can be left blank
    description = TextAreaField('Description')
    # url: can be left blank, otherwise must be a valid URL
    url = URLField('(Optional) URL')
    # address: required
    address = StringField('Address', validators=InputRequired())
    # city_code: must be drop-down menu of the cities in the db
    city_code = SelectField("City Code", coerce=int) # TODO: set this up to be dynamic and pull from DB
    # image_url: can be left blank, otherwise must be a valid URL
    image_url = URLField('(Optional) Image URL')


class CSRFOnlyForm(FlaskForm):
    """ CSRF only form. """