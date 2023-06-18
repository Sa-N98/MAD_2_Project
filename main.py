import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask , render_template ,request, redirect, url_for
from flask_security import Security, SQLAlchemyUserDatastore, login_required, UserMixin , RoleMixin
from flask_security.utils import hash_password

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY']='superseccret'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(current_dir, "database.sqlite3")
app.config['SECURITY_PASSWORD_SALT'] = 'salt'


db = SQLAlchemy()
db.init_app(app)

app.app_context().push()




class users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, autoincrement=True,  primary_key=True, nullable=False)
    username = db.Column(db.String, unique=True)
    email= db.Column(db.String,unique=True)
    password = db.Column(db.String)
    active = db.Column(db.Boolean)
    fs_uniquifier = db.Column(db.String)
    roles = db.relationship('role', secondary='roles_users', backref=db.backref('users', lazy= 'dynamic'))

class roles_users(db.Model):
      __tablename__ ='roles_users'
      user_id= db.Column(db.Integer, db.ForeignKey ('users.id'),primary_key=True, nullable=False)
      role_id=db.Column(db.Integer, db.ForeignKey ('role.id'), primary_key=True, nullable=False)


class role(db.Model,  RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
   
user_datastore=SQLAlchemyUserDatastore(db,users,None)
security=Security(app, user_datastore)

@app.route("/", methods=["GET", "POST"])
def hello_world():
    if request.method=="POST":
        user_datastore.create_user(
            username=request.form.get('username'),
            email=request.form.get('email'),
            password=hash_password(request.form.get('password')),
        )
        passwords=hash_password(request.form.get('password'))
        repasswords=hash_password(request.form.get('re-password'))
        print(passwords)
        print(repasswords)
        db.session.commit()
        return redirect (url_for('profile'))
    sas=users.query.all()
    return(render_template('landingPage.html', user=sas))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.hmtl')

if __name__ == '__main__':
    app.debug = True
    app.run()

