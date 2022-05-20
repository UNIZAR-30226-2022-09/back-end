class BaseConfig():
    SECRET_KEY = "YbFrbgHotPOI1HH64rNoJYSofLJJBFSS"
    DEBUG = True
    TESTING = True

class DevConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI='sqlite:///alejandria.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class ProConfig(BaseConfig):
    DEBUG = False
    TESTING = False