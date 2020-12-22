from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from sicm.config import DevConfig, ProdConfig


app = Flask(__name__)
app.config.from_object(DevConfig)

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

login_manager.login_view = "login"
login_manager.login_message = "Connnectez vous pour acceder au tableau da'administration"


from sicm.routes import *