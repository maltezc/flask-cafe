"""Data models for Flask Cafe"""


from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_USER_IMAGE_URL = "/static/images/default-pic.png"
DEFAULT_CAFE_IMAGE_URL = "/static/images/default-cafe.jpg"

# class Follows(db.Model):
#     """Connection of a follower <-> followed_user."""

#     __tablename__ = 'follows'

#     cafe_being_followed_id = db.Column(
#         db.Integer,
#         db.ForeignKey('users.id', ondelete="cascade"),
#         primary_key=True,
#     )

#     cafe_following_id = db.Column(
#         db.Integer,
#         db.ForeignKey('users.id', ondelete="cascade"),
#         primary_key=True,
#     )

class Like(db.Model):
    """Join table between users and cafes (the join represents a like)."""

    __tablename__ = 'likes'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
    )

    cafe_id = db.Column(
        db.Integer,
        db.ForeignKey('cafes.id', ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
    )


class City(db.Model):
    """Cities for cafes."""

    __tablename__ = 'cities'

    code = db.Column(
        db.Text,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    state = db.Column(
        db.String(2),
        nullable=False,
    )


class Cafe(db.Model):
    """Cafe information."""

    __tablename__ = 'cafes'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    url = db.Column(
        db.Text,
        nullable=False,
    )

    address = db.Column(
        db.Text,
        nullable=False,
    )

    city_code = db.Column(
        db.Text,
        db.ForeignKey('cities.code'),
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
        default=DEFAULT_CAFE_IMAGE_URL,
    )

    city = db.relationship("City", backref='cafes')

    liking_users = db.relationship("User", secondary="likes")

    def is_liking_cafe(self, current_user):
        """Does current user like the cafe?"""

        # get all users who currently like the cafe
        found_user_list = [
            user for user in self.liking_users if user == current_user
        ]
        return len(found_user_list) == 1

        #  if user is found, remove user, if not add the user


    def like_cafe(self, user):
        if not self.is_liking_cafe(user):
            self.liking_users.append(user)
            return self

    def unlike_cafe(self, user):
        if self.is_liking_cafe(user):
            self.liking_users.remove(user)
            return self



    def __repr__(self):
        return f'<Cafe id={self.id} name="{self.name}">'

    def get_city_state(self):
        """Return 'city, state' for cafe."""

        city = self.city
        return f'{city.name}, {city.state}'


    # `def is_liked_by(self, user):
    #     """Is this user followed by `other_user`?"""

    #     found_user_list = [
    #         user for user in Like.cafe_id if cafe_id == id]
    #     return len(found_user_list) == 1`


    # not sure if below is necessary
    # def serialize(self):
    #     """ Serialize message instance to python dictionary """

    #     return {
    #         "id": self.id,
    #         "name": self.name,
    #         # "user_id": g.user.user_id,
    #     }


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)



class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        # unique=True,
    )

    #TODO: ADMIN
    admin = db.Column(
        db.Boolean,
        nullable=True,
        default=False,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        # unique=True,
    )

    first_name = db.Column(
        db.String(100),
        nullable=False)

    last_name = db.Column(
        db.String(100),
        nullable=False)

    description = db.Column(
        db.String(100),
        nullable=False)

    image_url = db.Column(
        db.Text,
        default=DEFAULT_USER_IMAGE_URL,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    # reference: https://stackoverflow.com/questions/19598578/how-do-primaryjoin-and-secondaryjoin-work-for-many-to-many-relationship-in-s
    # liked_cafes = db.relationship(
    #     "Cafe",
    #     secondary="likes",
    #     primaryjoin=(Like.user_id == id),
    #     # primaryjoin=(Follows.cafe_being_followed_id == Cafe.id),
    #     secondaryjoin=(Like.cafe_id == Cafe.id),
    #     backref="liking_users",
    # )
    liked_cafes = db.relationship('Cafe', secondary="likes")



    # def like_cafe(self, cafe):
    #     if not self.is_liking_cafe(user):
    #         self.liked_cafes.append(user)
    #         return self

    # def unlike_cafe(self, cafe):
    #     if self.is_liking_cafe(user):
    #         self.liked_cafes.remove(user)
    #         return self



    def currently_likes(self, cafe):
        """does this user currently like the cafe?"""

        found_liked_cafes = [
            cafe for cafe in self.liking_users if cafe == cafe]
        return len(found_liked_cafes) == 1



    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"


    def get_full_name(self):
        """Returs user first name and last name"""
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def register(cls, username, first_name, last_name, description, email, password, admin=False, image_url=DEFAULT_USER_IMAGE_URL):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            admin=admin,
            first_name=first_name,
            last_name=last_name,
            description=description,
            email=email,
            password=hashed_pwd,
            image_url=image_url
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If this can't find matching user (or if password is wrong), returns
        False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False



