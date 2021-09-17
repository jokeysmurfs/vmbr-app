import os

WTF_CSRF_ENABLED = True
SECRET_KEY = '\xc2es\xc2(9N\xb3\xfc\xe1\x95\x00@\xf1K[F\xd43\xc9y\x1d\\\x91'

basedir = os.path.abspath(os.path.dirname(__file__)) 
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'DBrepository')