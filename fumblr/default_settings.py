import os

UPLOAD_FOLDER = 'fumblr/uploads'

DEBUG = os.environ.get('DEBUG', False)

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://Odysseus@localhost/fumblr')
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('DEBUG', False)