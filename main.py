import os
from application.model import *
from flask import Flask, render_template, request, redirect, url_for
from flask_security import Security, SQLAlchemyUserDatastore, login_required, logout_user, login_user
from flask_security.utils import hash_password, verify_password

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(current_dir, "database.sqlite3")
app.config['SECRET_KEY']='superseccret'
app.config['SECURITY_PASSWORD_SALT'] = 'salt'


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
         username = request.form['username']
         email = request.form['email']
         password = request.form['password']

         if form_type == 'login':
            user = User.query.filter_by(email=request.form.get('email')).first()
            if user and verify_password(password, user.password):
                login_user(user)
                return redirect(url_for('profile'))
            else:
                massage="User Not Found. Please Signup"
                return render_template('login_and_signup.html', massage=massage)
   
    return render_template('login_and_signup.html')


'''
This route is used for submition od the sign up form.
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
