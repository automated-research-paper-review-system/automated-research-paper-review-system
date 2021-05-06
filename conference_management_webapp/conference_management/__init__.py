from flask import Flask
import flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/conference_management'
app.config['MONGO_URI'] = 'mongodb+srv://karnavee:<>@researchpaper.yswis.mongodb.net/conference_management_system?retryWrites=true&w=majority'

mongo = PyMongo(app)
db = mongo.db
bcrypt = Bcrypt(app)

from conference_management_webapp.conference_management import routes