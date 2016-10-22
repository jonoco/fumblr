from flask import flash
from flask_login import LoginManager, current_user, login_user
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.contrib.twitter import make_twitter_blueprint
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from sqlalchemy.orm.exc import NoResultFound
from .models import User, OAuth
from .database import db
from .keys import TWITTER_KEY, TWITTER_SECRET, GOOGLE_ID, GOOGLE_SECRET

## create blueprints
backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)
twitter_blueprint = make_twitter_blueprint(api_key=TWITTER_KEY, api_secret=TWITTER_SECRET)
twitter_blueprint.backend = backend
google_blueprint = make_google_blueprint(client_id=GOOGLE_ID, client_secret=GOOGLE_SECRET, scope=["profile", "email"])
google_blueprint.backend = backend

## setup login manager
login_manager = LoginManager()
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flash('Failed to log in with {}'.format(blueprint.name))
        print('Error: Google oauth: No token received')
        return

    resp = blueprint.session.get('/plus/v1/people/me')
    if resp.ok and resp.text:
        email, x = resp.json()["emails"][0]["value"].split('@', 1)
        query = User.query.filter_by(loginname=email, provider='google')
        try:
            user = query.one()
        except NoResultFound:
            user = User(loginname=email, provider='google')
            db.session.add(user)
            db.session.commit()
        user.login()
        flash('Successfully signed in with Google')
    else:
        msg = 'Failed to fetch user info from {}'.format(blueprint.name)
        flash(msg, category='error')

@oauth_error.connect_via(google_blueprint)
def google_error(blueprint, message, response):
    msg = (
        "OAuth error from {name}! "
        "message={msg} response={resp} "
    ).format(name=blueprint.name, msg=message, resp=response)
    flash(msg, category='error')

# create/login local user on successful OAuth login
@oauth_authorized.connect_via(twitter_blueprint)
def twitter_logged_in(blueprint, token):
    if not token:
        flash('Failed to log in with {}'.format(blueprint.name))
        return
    # figure out who the user is
    resp = blueprint.session.get('account/settings.json')
    if resp.ok:
        username = resp.json()['screen_name']
        query = User.query.filter_by(loginname=username, provider='twitter')
        try:
            user = query.one()
        except NoResultFound:
            # create user
            user = User(loginname=username, provider='twitter')
            db.session.add(user)
            db.session.commit()
        user.login()
        flash('Successfully signed in with Twitter')
    else:
        msg = 'Failed to fetch user info from {}'.format(blueprint.name)
        flash(msg, category='error')

# notify on OAuth provider error
@oauth_error.connect_via(twitter_blueprint)
def twitter_error(blueprint, message, response):
    msg = (
        "OAuth error from {name}! "
        "message={msg} response={resp} "
        ).format(name=blueprint.name, msg=message, resp=response)
    flash(msg, category='error')




