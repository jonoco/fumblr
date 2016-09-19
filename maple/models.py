from .database import db
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import exists

tags = db.Table('tag_post_association',
                db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
                db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
                )

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(80))
    link = db.Column(db.String(80))
    deletehash = db.Column(db.String(80))
    created = db.Column(db.DateTime, default=datetime.utcnow)

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
    created = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('posts', lazy='dynamic'), uselist=False)

    image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    image = db.relationship('Image', backref=db.backref('post', uselist=False), uselist=False)

    tags = db.relationship('Tag', secondary=tags, backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, image, user, tags, text=None, created=None):
        self.image = image
        self.user = user
        self.text = text
        self.tags = tags
        self.created = created

    def __repr__(self):
        return '<Post {} - {}>'.format(self.user, self.image)

class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('likes', lazy='dynamic'), uselist=False)

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    post = db.relationship('Post', backref=db.backref('likes', lazy='dynamic'), uselist=False)


    def __init__(self, user, post, created=None):
        self.user = user
        self.post = post
        self.created = created

    def __repr__(self):
        return '<Like {} - {}>'.format(self.user, self.post)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    loginname = db.Column(db.String)
    provider = db.Column(db.String)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, loginname, provider, created=None):
        self.loginname = loginname
        self.provider = provider
        self.username = User.generate_username(loginname, id)
        self.created = created

    @classmethod
    def username_taken(cls, username):
        return db.session.query(exists().where(User.username == username)).scalar()

    @classmethod
    def generate_username(cls, loginname, id):
        """
        Generates a username for a user
        :param loginname:
        :param id:
        :return String:
        """
        if cls.username_taken(loginname):
            return '{name}{id}'.format(id=id,name=loginname)
        else:
            return loginname

    def get_user_info(self):
        return {
            'username': self.username
        }

    def following_user(self, username):
        """ Check if current user is following given user """
        return any(username == f.target.username for f in self.following)

    def follow_user(self, username):
        """ Follow user by given username and returns new Follow """

        user = User.query.filter_by(username=username).first()
        follow = Follow(target_user=user, follower_user=self)

        db.session.add(follow)
        db.session.commit()

        return follow

    def stop_following_user(self, username):
        """
            Deleted Follow for user provided
            Returns False if user wasn't found
        """
        follow = next(f for f in self.following if f.target.username == username)
        if follow:
            db.session.delete(follow)
            db.session.commit()
            return True
        else:
            return False

class Follow(db.Model):
    __tablename__ = 'followers'

    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    target = db.relationship('User', foreign_keys='Follow.target_id', backref=db.backref('followers', lazy='dynamic'), uselist=False)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    follower = db.relationship('User', foreign_keys='Follow.follower_id', backref=db.backref('following', lazy='dynamic'), uselist=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, target_user, follower_user, created=None):
        self.target = target_user
        self.follower = follower_user
        self.created = created

    def __repr__(self):
        return '<Follow {} - {}>'.format(self.target, self.follower)

class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, created=None):
        self.name = name
        self.created = created

    def __repr__(self):
        return '<Tag - {}>'.format(self.name)

class OAuth(db.Model, OAuthConsumerMixin):
    __tablename__ = 'oauths'

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

