import os
from application.model import *
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, PasswordField, SubmitField
from flask import Flask, render_template, request, redirect, url_for
from flask_security import Security, SQLAlchemyUserDatastore, login_required, logout_user, login_user
from flask_security.utils import hash_password

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(current_dir, "database.sqlite3")
app.config['SECRET_KEY']='superseccret'
app.config['SECURITY_PASSWORD_SALT'] = 'salt'


db.init_app(app)
app.app_context().push()

   

user_datastore=SQLAlchemyUserDatastore(db, User, Role)
security= Security(app, user_datastore)

@app.route("/", methods=['POST','GET'])
def index():
    if request.method =="POST":
        user_datastore.create_user(username=request.form.get('username'),
                                   email=request.form.get('email'),
                                   password= hash_password(request.form.get('password')))
        db.session.commit()
        return redirect(url_for('login'))
    hat="hat"
    return render_template('index.html',var=hat)

@app.route('/userlogin', methods=['GET', 'POST'])
def login():
    if request.method =='POST':
        print(request.form.get('email'))
        user = user_datastore.find_user(email=request.form.get('email'))
        login_user(user)
        return redirect(url_for('profile'))
    return render_template('login_user.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


# use this rout in link in template to log out 
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.debug = True
    app.run()
