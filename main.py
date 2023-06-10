import os
import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, abort
from sqlalchemy import and_

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(current_dir, "database.sqlite3")
api = Api(app)

# create the extension
db = SQLAlchemy()
# initialize the app with the extension
db.init_app(app)
app.app_context().push()





if __name__ == '__main__':
    app.debug = True
    app.run()

