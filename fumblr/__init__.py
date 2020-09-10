from flask import Flask
from fumblr.database import db
from fumblr.keys import APP_SECRET_KEY
from werkzeug.contrib.fixers import ProxyFix
from raven.contrib.flask import Sentry
from .default_settings import DEBUG

## initialize app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
Sentry(app)
app.secret_key = keys.APP_SECRET_KEY
app.config.from_pyfile('default_settings.py')

from fumblr import views
from fumblr import filters
from fumblr import admin
from .manager import twitter_blueprint, google_blueprint, login_manager

# hook up extensions
app.register_blueprint(twitter_blueprint, url_prefix='/login')
app.register_blueprint(google_blueprint, url_prefix='/login')
db.init_app(app)
login_manager.init_app(app)





