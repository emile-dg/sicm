
class DevConfig:
    SECRET_KEY = "5fda47368b295211f9ed41dd5b25afa7"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    
class ProdConfig:
    SECRET_KEY = "5fda47368b295211f9ed41dd5b25afa7"
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:emiledjida@localhost:5432/easylife"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False