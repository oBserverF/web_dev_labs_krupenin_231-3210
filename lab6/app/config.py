import os

SECRET_KEY = 'dev-key-change-this'
# SQLite DB in project folder (lab6.db)
SQLALCHEMY_DATABASE_URI = 'sqlite:///lab6.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    'media',
    'images'
)
