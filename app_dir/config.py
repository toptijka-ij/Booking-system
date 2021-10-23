import os

app_dir = os.path.abspath(os.path.dirname(__file__))
password = '22121'
host = 'localhost'
dbname = 'booking_system'


class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(20).hex()
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopementConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEVELOPMENT_DATABASE_URI') or f'postgresql://postgres:{password}@{host}/{dbname}'
