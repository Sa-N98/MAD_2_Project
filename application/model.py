from flask_sqlalchemy import SQLAlchemy
from flask_security import  UserMixin, RoleMixin
db = SQLAlchemy()



# This models is used for user sign up and login
roles_users= db.Table('roles_users',
                      db.Column('user_id', db.Integer, db.ForeignKey('User.id')),
                      db.Column('role_id', db.Integer, db.ForeignKey('Role.id'))
                      )
class User(db.Model,UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String,unique=True, nullable=False)
    password=db.Column(db.String)
    active=db.Column(db.Boolean)
    fs_uniquifier = db.Column(db.String)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users',lazy='dynamic'))

class Role(db.Model,RoleMixin):
    __tablename__ = 'Role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description= db.Column(db.String,nullable=False)


# This models is used for shows and venues
class show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, autoincrement=True,  primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    poster = db.Column(db.String, unique=False, nullable=False)
    posterLong = db.Column(db.String, unique=False, nullable=False)
    venue = db.relationship("venue", secondary="Show_Venue")
    dates = db.relationship("date", secondary="Show_Venue")
    genre = db.relationship("genre", secondary="movie_g")

class venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, autoincrement=True,
                   primary_key=True, unique=True)
    name = db.Column(db.String, unique=False, nullable=False)
    place = db.Column(db.String, unique=False, nullable=False)


class Show_Venue(db.Model):
    __tablename__ = 'Show_Venue'
    s_id = db.Column(db.Integer, db.ForeignKey("show.id"),
                     primary_key=True, nullable=False)
    v_id = db.Column(db.Integer, db.ForeignKey("venue.id"),
                     primary_key=True, nullable=False)
    d_id = db.Column(db.Integer, db.ForeignKey("date.id"),
                     primary_key=True, nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)


class movie_g(db.Model):
    __tablename__ = 'movie_g'
    m_id = db.Column(db.Integer, db.ForeignKey("show.id"),
                     primary_key=True, nullable=False)
    g_id = db.Column(db.Integer, db.ForeignKey("genre.id"),
                     primary_key=True, nullable=False)


class date(db.Model):
    __tablename__ = 'date'
    id = db.Column(db.Integer, autoincrement=True,
                   primary_key=True, unique=True)
    dates = db.Column(db.String, unique=True, nullable=False)


class genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, autoincrement=True,
                   primary_key=True, unique=True)
    type = db.Column(db.String, unique=True, nullable=False)

class booked_shows(db.Model):
    __tablename__ = 'booked_shows'
    id = db.Column(db.Integer, autoincrement=True,
                   primary_key=True, unique=True)
    user_name =db.Column(db.String)
    movieID = db.Column(db.Integer)
    venueID = db.Column(db.Integer)
    dateID = db.Column(db.Integer)
    NO_tickets = db.Column(db.Integer)
    



    