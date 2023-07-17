import os
from sqlalchemy import and_
from application.model import *
from application.api import*
from flask_security.utils import hash_password, verify_password
from flask_restful import Api
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_security import Security, SQLAlchemyUserDatastore, login_required, logout_user, login_user


current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(current_dir, "database.sqlite3")
app.config['SECRET_KEY'] = 'superseccret'
app.config['SECURITY_PASSWORD_SALT'] = 'salt'
app.jinja_options = app.jinja_options.copy()
app.jinja_options['variable_start_string'] = '[[ '
app.jinja_options['variable_end_string'] = ' ]]'


db.init_app(app)
app.app_context().push()

api = Api(app)
api.add_resource(show_booking, '/api/show_booking')
api.add_resource(show_cancel, '/api/show_cancel','/api/show_cancel/<bookind_id>')

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

'''
lodes the login and sign up page.
this route is also used for login validation.
'''


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        form_type = request.form['form_type']
        password = request.form['password']

        if form_type == 'login':
            user = User.query.filter_by(
                email=request.form.get('email')).first()
            if user and verify_password(password, user.password):
                login_user(user)
                return redirect(url_for('welcome'))
            else:
                massage = "User Not Found. Please Signup"
                return render_template('login_and_signup.html', massage=massage)

    return render_template('login_and_signup.html')


'''
This route is used for submition of the sign up form.
the form is submitted using js.
'''


@app.route('/submit', methods=['POST'])
def submit():
    user_datastore.create_user(username=request.form.get('username'),
                               email=request.form.get('email'),
                               password=hash_password(request.form.get('password')))
    db.session.commit()
    return "submition"


@app.route('/click')
def click():
    return "true"


@app.route('/api/movies')
def movies():
    last_five_rows = show.query.order_by(show.id.desc()).limit(5).all()
    last_five_movies_data = list()
    for data in last_five_rows:
        last_five_movies_data.append(
            {
                'name': data.name,
                'posterLong': data.posterLong,
                'poster': data.poster,
                'rating': data.rating,
            }
        )
    return jsonify(last_five_movies_data)


@app.route('/api/movie/<title>')
def movie(title):
    Show = show.query.filter(show.name == title).all()
    movie_data = {
        'id': Show[0].id,
        'poster': Show[0].poster,
        'rating': Show[0].rating,
    }
    print(movie_data)
    return jsonify(movie_data)


@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')
@app.route('/api/welcome')
@login_required
def show_data():
    movies=list()
    venues=list()
    genres=list()
    for movie in show.query.all():
        if len(movie.venue)>0:
            movies.append(movie.name)
    for movie_venue in venue.query.all():
            venues.append(movie_venue.name)
    for movie_genres in genre.query.all():
            genres.append(movie_genres.type)
    return {'movie_name':movies,
            'venues_name':venues,
            'genres':genres}

@app.route('/filter', methods=["GET", "POST"])
@login_required
def filter():
    if request.method == "POST":
        m_genre = request.form['genre']
        m_venue = request.form['place']
        m_rating = request.form['rating']
        title=list()
        if m_genre != 'none' and m_venue != 'none' and m_rating != 'none':
            for movie in show.query.filter(and_(show.genre.any(type=m_genre), 
                                                show.venue.any(name=m_venue), 
                                                show.rating.like(f'{m_rating}%'))).all():
                title.append(movie.name)
            json=[{'venue':m_venue ,
               'genre':m_genre,
               'rating': m_rating,
               'title':title
               }]
            return render_template('filter.html', data=json)
        elif m_genre != 'none' and m_venue != 'none' and m_rating == 'none':
           for movie in show.query.filter(and_(show.genre.any(type=m_genre),
                                               show.venue.any(name=m_venue))).all():
                title.append(movie.name)
           json=[{'venue':m_venue ,
               'genre':m_genre,
               'rating': m_rating,
               'title':title
               }]
           return render_template('filter.html', data=json)
        elif m_genre != 'none' and m_venue == 'none' and m_rating == 'none':
            for movie in show.query.filter(and_(show.genre.any(type=m_genre))).all():
                title.append(movie.name)
            json=[{'venue':m_venue ,
               'genre':m_genre,
               'rating': m_rating,
               'title':title
               }]
            return render_template('filter.html', data=json)
        elif m_genre == 'none' and m_venue != 'none' and m_rating == 'none':
            for movie in show.query.filter(and_(show.venue.any(name=m_venue))).all():
                title.append(movie.name)
            json=[{'venue':m_venue ,
               'genre':m_genre,
               'rating': m_rating,
               'title':title
               }]
            return render_template('filter.html', data=json)
        elif m_genre == 'none' and m_venue == 'none' and m_rating != 'none':
            for movie in show.query.filter(and_(show.rating.like(f'{m_rating}%'))).all():
                title.append(movie.name)
            json=[{'venue':m_venue ,
               'genre':m_genre,
               'rating': m_rating,
               'title':title
               }]
            return render_template('filter.html', data=json)
        elif m_genre != 'none' and m_venue == 'none' and m_rating != 'none':
            for movie in show.query.filter(and_(show.genre.any(type=m_genre), 
                                                show.rating.like(f'{m_rating}%'))).all():
                title.append(movie.name)
            json=[{'venue':m_venue ,
               'genre':m_genre,
               'rating': m_rating,
               'title':title
               }]
            return render_template('filter.html', data=json)
        elif m_genre == 'none' and m_venue != 'none' and m_rating != 'none':
            for movie in show.query.filter(and_(show.venue.any(name=m_venue), 
                                                show.rating.like(f'{m_rating}%'))).all():
                title.append(movie.name)
            json=[{'venue':m_venue ,
               'genre':m_genre,
               'rating': m_rating,
               'title':title
               }]
            return render_template('filter.html', data=json)


@app.route("/booking/<i>", methods=["GET", "POST"])
@login_required
def booking_page(i):
    if request.method == "GET":
        return render_template('booking.html')
    if request.method == "POST":
        return 'hi'
@app.route("/api/show-booking-data/<i>", methods=["GET", "POST"])
@login_required
def show_booking_data(i):
    movie = show.query.filter(show.id == i).first()
    infos = Show_Venue.query.filter(Show_Venue.s_id == i).all()
    venues = list()
    for venue in movie.venue:
        for date in movie.dates:
            for info in infos:
                if venue.id == info.v_id and date.id == info.d_id:
                    venues.append([[venue.id,venue.name, venue.place],
                                  [date.id, date.dates], 
                                  info.seats, 
                                  info.price, 
                                  movie.id]
                                 )
    shows = {
        'name': movie.name,
        'poster': movie.poster,
        'posterLong': movie.posterLong,
        'venues': venues
    }
    return jsonify(shows)

@app.route('/user_bookings/<current_user>', methods=["GET", "POST"])
@login_required
def user_bookings(current_user):
    infos=booked_shows.query.filter(booked_shows.user_name == current_user).all()
    shows_booked_by_users=list()
    for info in infos:
        # print(show.query.filter(show.id == info.movieID).first().name)

       movie_name=show.query.filter(show.id == info.movieID).first().name
       movie_poster=show.query.filter(show.id == info.movieID).first().poster
       venue_name=venue.query.filter(venue.id == info.venueID).first().name
       venue_place=venue.query.filter(venue.id == info.venueID).first().place
       movie_dates=date.query.filter(date.id == info.dateID).first().dates
       tickets=info.NO_tickets 
       ids=[
           info.id,
           show.query.filter(show.id == info.movieID).first().id,
           venue.query.filter(venue.id == info.venueID).first().id,
           date.query.filter(date.id == info.dateID).first().id
       ]
       shows_booked_by_users.append([movie_name,movie_poster,venue_name,venue_place,movie_dates,tickets,ids])

    return render_template('user_booking.html', data=shows_booked_by_users)


# use this rout in link in template to log out


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.debug = True
    app.run()
