"""Flask App for Flask Cafe."""

from flask import Flask, render_template, redirect, flash, session, g, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import os

from models import db, connect_db, Cafe, City, User, DEFAULT_USER_IMAGE_URL, Like
from forms import CafeAddUpdateForm, UserAddForm, LoginForm, CSRFOnlyForm, ProfileEditForm
from helpers import get_choices_vocab


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flaskcafe'
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "shhhh")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True

toolbar = DebugToolbarExtension(app)

connect_db(app)


#necessary for token in base.html: axios.defaults.headers.common["X-CSRFToken"] = "{{ csrf_token() }}";
#for how to use csrf_token with axios
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

######################################################################################
# auth & auth routes

CURR_USER_KEY = "curr_user"
NOT_LOGGED_IN_MSG = "You are not logged in."


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

@app.before_request
def add_csrf_only_form():
    """Add a CSRF-only form so that every route can use it."""

    g.csrf_form = CSRFOnlyForm()


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


# TODO: drop entire db and reseed.
# GET /signup
# Show registration form.
# POST /signup
# Process registration; if valid, adds user and then log them in. Redirects to cafe list with flashed message “You are signed up and logged in.”
@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                description=form.description.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            # flash("Username already taken")
            flash("Username already taken", 'danger')
            return render_template('auth/signup-form.html', form=form)

        do_login(user)
        flash("You are signed up and logged in.", "success")

        return redirect("/")

    else:
        return render_template('auth/signup-form.html', form=form)

# GET /login
# Show login form.
# POST /login
# Process login; if valid, logs user in and redirects to wcafe list with flashed message “Hello, USERNAME!”
@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login and redirect to homepage on success."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            form.username.data,
            form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('auth/login-form.html', form=form)


# POST /logout
# Process logout. Redirects to homepage with flashed message “You should have successfully logged out.”
@app.post('/logout')
def logout():
    """Handle logout of user and redirect to homepage."""

    form = g.csrf_form

    if not form.validate_on_submit() or not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/login")

##############################################################################################
# User page routes

# GET /profile
    # Show profile page.
@app.get('/profile')
def user_detail_page():
    """Shows user's profile page"""

    if not g.user:
        flash("Access unauthorized. NOT_LOGGED_IN", "danger")
        return redirect("/login")

    user = g.user
    # user = User.query.get_or_404(g.user.id)

    return render_template("/users/detail.html", user=user)


# GET /profile/edit
    # Show profile edit form.
# POST /profile/edit
    # Process profile edit. On success, this should redirect to the profile page with the flashed message “Profile edited.”
@app.route('/profile/edit', methods=["GET", "POST"])
def edit_profile():
    """Form editing a user's profile page"""

    if not g.user:
        flash("Access unauthorized. NOT_LOGGED_IN", "danger")
        return redirect("/login")

    user = g.user
    form = ProfileEditForm(obj=user)

    if form.validate_on_submit():
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.description = form.description.data
        user.image_url = form.image_url.data or DEFAULT_USER_IMAGE_URL

        db.session.commit()
        flash("Profile edited.", "success")
        return redirect(f"/profile")


    return render_template('users/edit.html', form=form, user=user)



######################################################################################
# homepage

@app.get("/")
def homepage():
    """Show homepage."""

    return render_template("homepage.html")


##############################################################################################
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
@app.route('/cafes/add', methods=["GET", "POST"])
def add_cafe():
    """Form for adding a cafe"""

    form = CafeAddUpdateForm()
    city_codes = get_choices_vocab()
    # city_codes = [(city.code, city.name) for city in City.query.all()]
    form.city_code.choices = city_codes

    # breakpoint()

    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        url = form.url.data
        address = form.address.data
        image_url = form.image_url.data
        cafe = Cafe(name=name, description=description, url=url, address=address, city_code=form.city_code.data, image_url=image_url)

        db.session.add(cafe)
        db.session.commit()

        flash(f"{cafe.name} added!")

        return redirect(f'/cafes/{cafe.id}')

    return render_template("/cafe/add-form.html", form=form)


# GET /cafes/[cafe-id]/edit
# Show form for editing cafe
# POST /cafes/[cafe-id]/edit
# Handle editing cafe. On success, redirect to cafe detail page with flash message “CAFENAME edited.”
@app.route('/cafes/<int:cafe_id>/edit', methods=["GET", "POST"])
def edit_cafe(cafe_id):
    """Shows form for editing cafe info"""

    cafe = Cafe.query.get_or_404(cafe_id)
    form = CafeAddUpdateForm(obj=cafe)

    city_codes = get_choices_vocab()
    form.city_code.choices = city_codes


    if form.validate_on_submit():

        cafe.name = form.data.get("name", cafe.name)
        cafe.description = form.data.get("description", cafe.description)
        cafe.url = form.data.get("url", cafe.url)
        cafe.address = form.data.get("address", cafe.address)
        cafe.city_code = form.data.get("city_code", cafe.city_code)
        cafe.image_url = form.data.get("image_url", cafe.image_url)

        db.session.commit()

        flash(f"{cafe.name} edited")
        return redirect(f"/cafes/{cafe.id}")

    return render_template("/cafe/edit-form.html", form=form, cafe=cafe)


# GET /api/likes
# Given cafe_id in the URL query string, figure out if the current user likes that cafe, and return JSON: {"likes": true|false}
@app.get('/api/likes')
def get_likes():
    """checks to like status of cafe for the user"""

    if not g.user:
        return jsonify({"error": "Not logged in"})

    cafe_id = int(request.args['cafe_id'])
    cafe = Cafe.query.get_or_404(cafe_id)

    like = Like.query.filter_by(user_id=g.user.id, cafe_id=cafe.id).first()
    likes = like is not None

    return jsonify({"likes": likes})




# POST /api/like
# Given JSON {"cafe_id": 1}, make the current user like cafe #1. Return JSON {"liked": 1}.
# POST /api/unlike
# Given JSON {"cafe_id": 1}, make the current user unlike cafe #1. Return JSON {"unliked": 1}.

@app.post('/api/toggle_like/<int:cafe_id>')
# @app.post('/messages/<int:message_id>/like')
def toggle_like(cafe_id):
    """Toggle a cafe like status for the currently-logged-in user.
    """

    if not g.user:
        return jsonify({"error": "Not logged in"})

    cafe = Cafe.query.get_or_404(cafe_id)

    form = g.csrf_form

    if not form.validate_on_submit() or not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    if g.user in cafe.liking_users:
        cafe.unlike_cafe(g.user)
        status = {"unliked": cafe_id}
        db.session.commit()
        return jsonify(status)

    else:
        cafe.like_cafe(g.user)
        status = {"liked": cafe_id}
        db.session.commit()
        return jsonify(status)




    # if cafe in g.user.liked_cafes:
    #     g.user.liked_messages.remove(message)
    # else:
    #     g.user.liked_messages.append(message)
    #     is_msg_liked = True



    # serialized = cafe.serialize()
    # serialized["is_liked"] = is_cafe_liked

    # return ((status), 201)
    # return (jsonify(message=serialized), 201)



    # Identify the url the user is coming from via the hidden input. We can
    # redirect them back to this location for a better user experience. Added
    # the default of "/" so the app doesn't crash in the event that a template is
    # added/changed and someone forgets to include that hidden input element.
    # redirection_url = request.form.get("came_from", "/")

    # if cafe.user_id == g.user.id:
    #     return abort(403) # doesnt apply

    # if g.user in cafe.liking_users:
    #     cafe.unlike_cafe(g.user)
    # else:
    #     cafe.like_cafe(g.user)

    # db.session.commit()

    # return redirect(redirection_url)


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(response):
    """Add non-caching headers on every request."""

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
    response.cache_control.no_store = True
    return response