import os

UPLOAD_FOLDER = 'fumblr/uploads'

DEBUG = os.environ.get('DEBUG', False)
PORT = os.environ.get('PORT', 5000)

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://Odysseus@localhost/maple')
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('DEBUG', False)