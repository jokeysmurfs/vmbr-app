import os
from flask import Flask
from config import basedir
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)    #app instance
app.config.from_object('config') #app configuration file
db = SQLAlchemy(app)

