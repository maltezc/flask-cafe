"""Flask App for Flask Cafe."""

from flask import Flask, render_template, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
import os

from models import db, connect_db, Cafe, City
from forms import CafeAddUpdateForm


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flaskcafe'
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "shhhh")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True

toolbar = DebugToolbarExtension(app)

connect_db(app)

#######################################
# auth & auth routes

CURR_USER_KEY = "curr_user"
NOT_LOGGED_IN_MSG = "You are not logged in."


# @app.before_request
# def add_user_to_g():
#     """If we're logged in, add curr user to Flask global."""

#     if CURR_USER_KEY in session:
#         g.user = User.query.get(session[CURR_USER_KEY])

#     else:
#         g.user = None


# def do_login(user):
#     """Log in user."""

#     session[CURR_USER_KEY] = user.id


# def do_logout():
#     """Logout user."""

#     if CURR_USER_KEY in session:
#         del session[CURR_USER_KEY]


#######################################
# homepage

@app.get("/")
def homepage():
    """Show homepage."""

    return render_template("homepage.html")


#######################################
# cafes


@app.get('/cafes')
def cafe_list():
    """Return list of all cafes."""

    cafes = Cafe.query.order_by('name').all()

    return render_template('cafe/list.html', cafes=cafes)


@app.get('/cafes/<int:cafe_id>')
def cafe_detail(cafe_id):
    """Show detail for cafe."""

    cafe = Cafe.query.get_or_404(cafe_id)

    return render_template('cafe/detail.html', cafe=cafe)

# GET /cafes/add
# Show form for adding a cafe
# POST /cafes/add
# Handle adding new cafe. On success, redirect to new cafe detail page with flash message “CAFENAME added.”
@app.routes('/cafes/add', methods=["GET", "POST"])
def add_cafe():
    """Form for adding a cafe"""

    form = CafeAddUpdateForm()
    city_codes = [(city.id, city.name) for city in City.query.all()]

    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        url = form.url.data
        address = form.address.data
        city_code = form.city_code.data # TODO: set up selction field.
        image_url = form.image_url.data

        cafe = Cafe(name, description, url, address, city_code, image_url)

        db.session.add(cafe)
        db.session.commit()

        flash(f"{cafe.name} added!")

        return redirect(f'/cafes/{cafe.id}')

    return render_template("add-form.html", form=form)


# GET /cafes/[cafe-id]/edit
# Show form for editing cafe
# POST /cafes/[cafe-id]/edit
# Handle editing cafe. On success, redirect to cafe detail page with flash message “CAFENAME edited.”
@app.routes('/cafes/<int:cafe_id', methods=["GET", "POST"])
def edit_cafe(cafe_id):
    """Shows form for editing cafe info"""

    cafe = Cafe.query.get_or_404(cafe_id)
    form = CafeAddUpdateForm(obj=cafe)

    if form.validate_on_submit():

        cafe.name = form.data.get("name", cafe.name)
        cafe.description = form.data.get("description", cafe.description)
        cafe.url = form.data.get("url", cafe.url)
        cafe.address = form.data.get("address", cafe.address)
        cafe.city_code = form.data.get("city_code", cafe.city_code)
        cafe.image_url = form.data.get("image_url", cafe.image_url)

        flash(f"{cafe.name} edited")
        return redirect(f"/cafe/{cafe.id}")

    return render_template("cafe/edit-form.html", form=form)