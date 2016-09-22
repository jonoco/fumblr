from flask import Flask
from fumblr.database import db
from .keys import *

## initialize app
app = Flask(__name__)
app.secret_key = keys.APP_SECRET_KEY
app.config.from_pyfile('default_settings.py')

from fumblr import views
from .manager import twitter_blueprint, google_blueprint, login_manager

# hook up extensions
app.register_blueprint(twitter_blueprint, url_prefix='/login')
app.register_blueprint(google_blueprint, url_prefix='/login')
db.init_app(app)
login_manager.init_app(app)








