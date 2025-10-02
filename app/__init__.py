from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

import os
load_dotenv('.env')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['UPLOAD_FILES'] = r'static/data'
 
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager (app)
login_manager.login_view = 'LoginPage'
bcrypt = Bcrypt(app)

from .models import User 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
 
from .view import homepage
