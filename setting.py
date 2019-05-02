import os

class Config():
    # Ключ лучше сохранять в системные переменные
    SECRET_KEY =  os.environ.get("SECRET_KEY") or "fj2w02@!bbgq`@SDu1jqdq65wq3(*!@K!54LMQO2eqwdq6wqe6q4q"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "postgresql://user:1234@127.0.0.1:5432/wow_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PAZZ = "88051-9019"
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False