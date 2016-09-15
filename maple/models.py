from .database import db
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin
from flask_login import UserMixin

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(80))
    link = db.Column(db.String(80))
    deletehash = db.Column(db.String(80))
    created = db.Column(db.DateTime)

    def __init__(self, image, deletehash, link, created=None):
        self.image = image
        self.deletehash = deletehash
        self.link = link
        self.created = created

    def __repr__(self):
        return '<Image {}>'.format(self.image)

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String())
    created = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    #user = db.relationship('User', backref=db.backref('user', lazy='joined'), uselist=False)

    image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    image = db.relationship('Image', backref=db.backref('image', lazy='joined'), uselist=False)

    def __init__(self, image, user, text=None, created=None):
        self.image = image
        self.user = user
        self.text = text
        self.created = created

    def __repr__(self):
        return '<Post {} - {}>'.format(self.user, self.image)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    created = db.Column(db.DateTime)
    posts = db.relationship('Post', backref='user', lazy='dynamic')

    def __init__(self, username, created=None):
        self.username = username
        self.created = created

class OAuth(db.Model, OAuthConsumerMixin):
    __tablename__ = 'oauths'

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

