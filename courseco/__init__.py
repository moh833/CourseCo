import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = '2377c5f97f4c5c7bebbed4587f214707'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
SQLALCHEMY_TRACK_MODIFICATIONS = False
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
# pass the name of the login func to be redirected to when trying to access login_required pages
login_manager.login_view = 'login'
# the bootstrap class of the message displayed when trying to access login_required pages whithout logging in
login_manager.login_message_category = 'info'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '' # os.environ.get('username')
app.config['MAIL_PASSWORD'] = '' # os.environ.get('password')
mail = Mail(app)

from courseco import routes
