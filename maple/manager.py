from flask import flash
from flask_login import LoginManager, current_user, login_user
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.contrib.twitter import make_twitter_blueprint
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from sqlalchemy.orm.exc import NoResultFound
from .models import User, OAuth
from .database import db
from .keys import TWITTER_SECRET, TWITTER_KEY

## create blueprints
twitter_blueprint = make_twitter_blueprint(api_key=TWITTER_KEY, api_secret=TWITTER_SECRET)
twitter_blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)

## setup login manager
login_manager = LoginManager()
login_manager.login_view = 'twitter.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
        query = User.query.filter_by(username=username)
        try:
            user = query.one()
        except NoResultFound:
            # create user
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        login_user(user)
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




