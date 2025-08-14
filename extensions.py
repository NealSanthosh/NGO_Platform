# extensions.py
from flask_pymongo import PyMongo
from flask_login import LoginManager

# Initialize extensions without app binding
mongo = PyMongo()
login_manager = LoginManager()
