import os
from sqlalchemy import and_
from application.model import *
from flask_security.utils import hash_password, verify_password
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_security import Security, SQLAlchemyUserDatastore, login_required, logout_user, login_user



current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(current_dir, "database.sqlite3")
app.config['SECRET_KEY']='superseccret'
app.config['SECURITY_PASSWORD_SALT'] = 'salt'
app.jinja_options = app.jinja_options.copy()
app.jinja_options['variable_start_string'] = '[[ '
app.jinja_options['variable_end_string'] = ' ]]'


db.init_app(app)
app.app_context().push()


user_datastore=SQLAlchemyUserDatastore(db, User, Role)
security= Security(app, user_datastore)

'''
lodes the login and sign up page.
this route is also used for login validation.
'''
@app.route("/", methods=['POST','GET'])
def index():
    if request.method =="POST":
         form_type = request.form['form_type']
         password = request.form['password']

         if form_type == 'login':
            user = User.query.filter_by(email=request.form.get('email')).first()
            if user and verify_password(password, user.password):
                login_user(user)
                return redirect(url_for('welcome'))
            else:
                massage="User Not Found. Please Signup"
                return render_template('login_and_signup.html', massage=massage)
   
    return render_template('login_and_signup.html')


'''
This route is used for submition of the sign up form.
the form is submitted using js.
'''
@app.route('/submit',methods=['POST'])
def submit():
    user_datastore.create_user(username=request.form.get('username'),
                                    email=request.form.get('email'),
                                   password= hash_password(request.form.get('password')))
    db.session.commit()
    return "submition"


@app.route('/click')
def click():
    return "true"

@app.route('/api/movies')
def movies():
    last_five_rows = show.query.order_by(show.id.desc()).limit(5).all()
    last_five_movies_data = list()
    for data in  last_five_rows :
        last_five_movies_data.append(
            {
            'name':data.name,
            'posterLong':data.posterLong,
            'poster':data.poster,
            'rating':data.rating,
             }
        )
    return jsonify(last_five_movies_data)

@app.route('/api/movie/<title>')
def movie(title):
    Show = show.query.filter(show.name == title).all()
    movie_data= {
            'name': Show[0].name,
            'poster':Show[0].poster,
            'rating':Show[0].rating,
            }
    print(movie_data) 
    return jsonify(movie_data)

@app.route('/welcome')
@login_required
def welcome():
    movie = show.query.all()
    venues = venue.query.all()
    genres = genre.query.all()
    return render_template('welcome.html' , movies=movie , venue=venues, genre=genres)

@app.route('/filter', methods=["GET", "POST"])
@login_required
def filter():
    if request.method == "POST":
        m_genre = request.form['genre']
        m_venue = request.form['place']
        m_rating = request.form['rating']
        if m_genre != 'none' and m_venue != 'none' and m_rating != 'none':
            movie = show.query.filter(and_(show.genre.any(type=m_genre), show.venue.any(
                name=m_venue), show.rating.like(f'{m_rating}%'))).all()
            return render_template('filter.html', g=m_genre, v=m_venue, r=m_rating, movies=movie)
        elif m_genre != 'none' and m_venue != 'none' and m_rating == 'none':
            movie = show.query.filter(
                and_(show.genre.any(type=m_genre), show.venue.any(name=m_venue))).all()
            return render_template('filter.html', g=m_genre, v=m_venue, r=m_rating, movies=movie)
        elif m_genre != 'none' and m_venue == 'none' and m_rating == 'none':
            movie = show.query.filter(and_(show.genre.any(type=m_genre))).all()
            return render_template('filter.html', g=m_genre, v=m_venue, r=m_rating, movies=movie)
        elif m_genre == 'none' and m_venue != 'none' and m_rating == 'none':
            movie = show.query.filter(and_(show.venue.any(name=m_venue))).all()
            return render_template('filter.html', g=m_genre, v=m_venue, r=m_rating, movies=movie)
        elif m_genre == 'none' and m_venue == 'none' and m_rating != 'none':
            movie = show.query.filter(
                and_(show.rating.like(f'{m_rating}%'))).all()
            return render_template('filter.html', g=m_genre, v=m_venue, r=m_rating, movies=movie)
        elif m_genre != 'none' and m_venue == 'none' and m_rating != 'none':
            movie = show.query.filter(
                and_(show.genre.any(type=m_genre), show.rating.like(f'{m_rating}%'))).all()
            return render_template('filter.html', g=m_genre, v=m_venue, r=m_rating, movies=movie)
        elif m_genre == 'none' and m_venue != 'none' and m_rating != 'none':
            movie = show.query.filter(
                and_(show.venue.any(name=m_venue), show.rating.like(f'{m_rating}%'))).all()
            return render_template('filter.html', g=m_genre, v=m_venue, r=m_rating, movies=movie)
  


# use this rout in link in template to log out 
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.debug = True
    app.run()
