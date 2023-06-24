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