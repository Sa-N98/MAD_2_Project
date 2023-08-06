import os
import csv
import requests
from sqlalchemy import and_
from application.model import *
from application.api import*
from flask_security.utils import hash_password, verify_password
from flask_restful import Api
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from flask_security import Security, SQLAlchemyUserDatastore, login_required, logout_user, login_user
from werkzeug.utils import secure_filename
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from celery_worker import make_celery
from celery.result import AsyncResult
from celery.schedules import crontab
from datetime import timedelta
from Email import send_email
from datetime import datetime
import calendar





current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(current_dir, "database.sqlite3")
app.config['SECRET_KEY'] = 'superseccret'
app.config['SECURITY_PASSWORD_SALT'] = 'salt'
app.jinja_options = app.jinja_options.copy()
app.jinja_options['variable_start_string'] = '[[ '
app.jinja_options['variable_end_string'] = ' ]]'
app.config['JWT_SECRET_KEY'] = 'TOP_secret_key' 
UPLOAD_FOLDER = "static/Images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    result_backend='redis://localhost:6379'
)

db.init_app(app)
jwt = JWTManager(app)
celery = make_celery(app)
app.app_context().push()




api = Api(app)
api.add_resource(show_booking, '/api/show_booking')
api.add_resource(show_cancel, '/api/show_cancel','/api/show_cancel/<bookind_id>')
api.add_resource(venue_update, '/api/venue','/api/venue/<venue_id>')
api.add_resource(show_update, '/api/show','/api/show/<sid>/<vid>/<did>')

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
            if user and user.role=='user' and verify_password(password, user.password):
                login_user(user)
                user.log_login()
                global access_token
                access_token = create_access_token(identity=user.email)
                return redirect(url_for('welcome', access_token=access_token))
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
                               role=request.form.get('user_type'),
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
    # print(movie_data)
    return jsonify(movie_data)


@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html',access_token=access_token)
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

############ admin ############

@app.route("/admin", methods=['POST', 'GET'])
def admin():
    if request.method == "POST":
        form_type = request.form['form_type']
        password = request.form['password']

        if form_type == 'login':
            user = User.query.filter_by(
                email=request.form.get('email')).first()
            if user and user.role=='admin' and verify_password(password, user.password):
                login_user(user)
                global access_token_admin
                access_token_admin = create_access_token(identity=user.email)
                return redirect(url_for('dashbord', access_token=access_token_admin))
            else:
                massage = "Admin Not Found. Please Signup"
                return render_template('admin.html', massage=massage)

    return render_template('admin.html')

@app.route("/dashbord", methods=['POST', 'GET'])
@login_required
def dashbord():
    infos = Show_Venue.query.all()
    total_seats=0
    for info in infos:
        total_seats=total_seats + info.starting_seats

    temp=dict()
    for info in infos:
        if info.s_id not in temp.keys():
            temp[info.s_id]=0
        if  info.s_id in temp.keys():
            temp[info.s_id]=temp[info.s_id]+(info.starting_seats-info.seats)
    venue_temp=dict()
    for info in infos:
        if info.v_id not in venue_temp.keys():
            venue_temp[info.v_id]=0
        if  info.v_id in temp.keys():
            venue_temp[info.v_id]=venue_temp[info.v_id]+(info.starting_seats-info.seats)
    max_key = max(venue_temp, key=venue_temp.get)
    top_venue=[venue.query.filter(venue.id==max_key).first().name,venue.query.filter(venue.id==max_key).first().place]
    max_bookings=venue_temp[max_key]

    movie_name=list()
    tickets=list()
    for key in temp.keys():
        movie_name.append(show.query.filter(show.id == key).first().name)
        tickets.append(temp[key])

    booking_info = booked_shows.query.all()
    tickets_sold=0
    for info in booking_info:
        tickets_sold=tickets_sold + info.NO_tickets
    
    poster=show.query.filter(show.name == movie_name[tickets.index(max(tickets))]).first().poster
    print(poster)
   
    users=len(User.query.filter(User.role=='user').all())
    
    venuue_data=list()
    v_tmp=venue.query.all()
    for v in v_tmp:
        venuue_data.append([v.id,v.name,v.place])
    
    show_data=list()
    for shows in show.query.all():
        for dates in date.query.all():
            for info in infos:
                for v in v_tmp:
                    if shows.id==info.s_id and v.id==info.v_id and dates.id==info.d_id:
                        show_data.append([shows.name,v.name,v.place,info.seats,dates.dates,info.price,[info.s_id,info.v_id,info.d_id]])


    data={
        "movie_name":movie_name,
        "tickets":tickets,
        "pidata": [total_seats, tickets_sold],
        "poster":poster,
        'top_venue':top_venue,
        'max_bookings':max_bookings,
        'users':users,
        'venuue_data':venuue_data,
        'show_data':show_data
        }

    return render_template('dashbord.html',data=data,access_token=access_token_admin)

@app.route("/admin/update_venue", methods=['POST', 'GET'])
@login_required
def update_venue():
    return render_template('add_venue.html')

@app.route("/api/update_venue_data", methods=['POST', 'GET'])
@login_required
def venue_data():
    venuue_data=list()
    v_tmp=venue.query.all()
    for v in v_tmp:
        venuue_data.append([v.id,v.name,v.place])
    return venuue_data

@app.route("/admin/update_show", methods=['POST', 'GET'])
@login_required
def update_show():
    return render_template('add_show.html')

@app.route("/api/update_show_data", methods=['POST', 'GET'])
@login_required
def shows_data():
    show_data=list()
    query_result = Show_Venue.query\
                    .join(show, Show_Venue.s_id == show.id)\
                    .join(venue, Show_Venue.v_id == venue.id)\
                    .join(date, Show_Venue.d_id == date.id)\
                    .with_entities(show.name, venue.name, venue.place, date.dates, Show_Venue.seats, Show_Venue.price,Show_Venue.s_id,Show_Venue.v_id,Show_Venue.d_id)\
                    .all()

    for data in query_result:
        show_data.append([data[0], data[1], data[2], data[3], data[4], data[5],[data[6],data[7],data[8]]])
    return show_data


@app.route('/upload', methods=["POST"])
@login_required
@jwt_required()
def upload():
    form_id = request.form.get('form_id')
    Movie = request.form.get('Movie')
    place = request.form.get('place')
    ratings = request.form.get('rating')
    seats = request.form.get('seats')
    price = request.form.get('price')
    date = request.form.get('date')
    movie_genre=request.form.get('genre')
    if form_id=='upload':
        banner_file = request.files['banner']
        poster_file = request.files['poster']
        banner_filename = secure_filename(banner_file.filename)
        poster_filename = secure_filename(poster_file.filename)
        if banner_filename.split('.')[-1].lower() in ['jpeg','png','jpg','webp']:
            banner_path = os.path.join(app.config['UPLOAD_FOLDER'], banner_filename)
            banner_file.save('C:\\Users\\Sharonno\\Desktop\\MAD-2 project\\MAD_2_Project\\static\\Images\\'+banner_filename)
        else:
            return jsonify(error="Invalid file extension for banner. Allowed extensions are: " + ', '.join(['jpeg','png','jpg','webp'])), 400

        if poster_filename.split('.')[-1].lower() in ['.jpeg','png','jpg','webp']:
            poster_path = os.path.join(app.config['UPLOAD_FOLDER'], poster_filename)
            poster_file.save('C:\\Users\\Sharonno\\Desktop\\MAD-2 project\\MAD_2_Project\\static\\Images\\' + poster_filename)
        else:
            return jsonify(error="Invalid file extension for banner. Allowed extensions are: " + ', '.join(['jpeg','png','jpg','webp'])), 400
    
    hostname = request.host.split(':')[0]
    port = request.host.split(':')[1]

    url = f'http://{hostname }:{port}/api/show'
    headers = {"Authorization": f"Bearer {access_token_admin}"}
    
    if form_id=='upload':
        data = { 'place': place,
                'movie':Movie,
                'posterURL': '\\static\\Images\\' + poster_filename,
                'bannerURL': '\\static\\Images\\' + banner_filename,
                'date': date,
                'rating': ratings,
                'seats': seats,
                'price': price,
                'genre':movie_genre
            }
        requests.post(url, json=data,headers=headers)
    if form_id=='update':
        data = { 'place': place,
                'movie':Movie,
                'date': date,
                'rating': ratings,
                'seats': seats,
                'price': price
            }
        requests.put(url, json=data, headers=headers)
    
    return 'upload success'



@app.route('/test',methods=["POST","GET"])
def test_page():
    return render_template("test.html")


############################# CELERY ##################################################
import time

@celery.task
def generate_csv(id):
    # time.sleep(6)
    rows=list()
    venue_raw_data=Show_Venue.query.filter(Show_Venue.v_id==id).all()
    for data in venue_raw_data:
        name=show.query.filter(show.id==data.s_id).first().name
        show_date=date.query.filter(date.id==data.d_id).first().dates
        rows.append([name, show_date, data.starting_seats, data.seats, data.price])
   
    fields = ['Name', 'Date', 'Seats At Start', 'Seats','Price']
    
    # writing to csv file
    with open("static/data.csv", 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        
        # writing the fields
        csvwriter.writerow(fields)
        
        # writing the data rows
        csvwriter.writerows(rows)

    return "Job Started..."

@app.route("/triger_celery_job/<id>")
def trigger_celery_job(id):
    a = generate_csv.delay(id)
    return {
        "Task_ID" : a.id,
        "Task_State" : a.state,
        "Task_Result" : a.result
    }

@app.route("/status/<id>")
def check_status(id):
    res = AsyncResult(id, app = celery)
    return {
        "Task_ID" : res.id,
        "Task_State" : res.state,
        "Task_Result" : res.result
    }

@app.route("/download-file")
def download_file():
    return send_file("static/data.csv")


@celery.task
def send_daily_reminder():
    users = User.query.filter_by(role='user').all()
    for user in users:
        current_date_time = datetime.now()
        time_difference = current_date_time - user.last_login
        if time_difference.days >= 1:
            message=render_template('dailey_html_template.html', user_name=user.username )
            send_email(to_address=user.email, subject="Reconnect with Showcase: Your Latest Movie Booking Update", message=message)
    


# celery.conf.beat_schedule = {
#     'my_periodic_task_schedule': {
#         'task': 'main.send_daily_reminder', 
#         'schedule': timedelta(seconds=5) 
#         # 'schedule': crontab(hour=13, minute=20)
#     },
# }


@celery.task
def monthley_report():
    users = User.query.filter_by(role='user').all()
    current_month = datetime.now().month
    month_name = calendar.month_name[current_month]
    for user in users:
        shows = booked_shows.query.filter_by(user_name=user.username).all()

        num_movies_booked=len(shows)

        num_tickets_bought=0
        for movie in shows:
            num_tickets_bought=num_tickets_bought + movie.NO_tickets
        
        shows_booked_by_users=list()

        for info in shows:
            movie_name=show.query.filter(show.id == info.movieID).first().name
            venue_name=venue.query.filter(venue.id == info.venueID).first().name
            movie_dates=date.query.filter(date.id == info.dateID).first().dates
            tickets=info.NO_tickets 
            shows_booked_by_users.append([movie_name,venue_name,movie_dates,tickets])

        message=render_template('monthley_report.html', 
                                month=month_name, 
                                num_movies_booked=num_movies_booked, 
                                num_tickets_bought=num_tickets_bought,
                                data = shows_booked_by_users )
        
        from weasyprint import HTML
        from io import BytesIO  
        pdf_bytes = BytesIO()
        HTML(string=message).write_pdf(target=pdf_bytes)
        pdf_bytes.seek(0)
        pdf_content = pdf_bytes.read()


        
        send_email(to_address=user.email, subject="🎬 Your Monthly Movie Booking Report from Showcase", message=message,attachment=pdf_content )


celery.conf.beat_schedule = {
    'my_periodic_task_schedule': {
        'task': 'main.monthley_report', 
        # 'schedule': timedelta(seconds=15) 
        'schedule': crontab(day_of_month=1, hour=0, minute=0)
    },

    'my_dayley_task_schedule': {
        'task': 'main.send_daily_reminder', 
        # 'schedule': timedelta(seconds=5) 
        'schedule': crontab(hour=13, minute=20)
    },
}

# use this rout in link in template to log out
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.debug = True
    app.run()
