from flask import current_app
from .database import db
from .services.imgur import upload_image
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin
from flask_login import UserMixin, current_user
from datetime import datetime
from sqlalchemy import exists, and_, or_
from werkzeug.utils import secure_filename
import os

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

    @staticmethod
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    @classmethod
    def submit_image(cls, file):
        """
        Example:

        {'size': 3527,
        'title': None,
        'animated': False,
        'deletehash': 'YkK79ucEtDDn1b9',
        'views': 0,
        'width': 187,
        'account_url': None,
        'in_gallery': False,
        'name': '',
        'section': None,
        'account_id': 0,
        'type': 'image/png',
        'datetime': 1473926225,
        'description': None,
        'height': 242,
        'bandwidth': 0,
        'id': 'AEvnA7h',
        'favorite': False,
        'nsfw': None,
        'link': 'http://i.imgur.com/AEvnA7h.png',
        'is_ad': False,
        'vote': None}

        :param file:
        :return Image:
        """

        image_path = cls.save_image(file)

        image_data = upload_image(image_path)
        image = Image(image_data['id'], image_data['deletehash'], image_data['link'])

        db.session.add(image)
        db.session.commit()

        cls.delete_image(file)

        return image

    @classmethod
    def save_image(cls, file):
        filename = secure_filename(file.filename)
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)

        return image_path

    @classmethod
    def delete_image(cls, file):
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        os.remove(image_path)

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('posts', lazy='dynamic'), uselist=False)

    image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    image = db.relationship('Image', backref=db.backref('post', uselist=False), uselist=False)

    tags = db.relationship('Tag', secondary=tags, backref=db.backref('posts', lazy='dynamic'))
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, image, user, tags, text=None, created=None):
        self.image = image
        self.user = user
        self.text = text
        self.tags = tags
        self.created = created

    def __repr__(self):
        return '<Post {} - {}>'.format(self.user, self.image)

    def get_data(self):
        return {
            'id': self.id,
            'link': self.image.link,
            'text': self.text or '',
            'user': self.user.get_user_info(),
            'likes': [l.get_data() for l in self.likes],
            'liked': self.is_liked(),
            'tags': [tag.name for tag in self.tags],
            'comments': [cmt.get_data() for cmt in self.comments],
            'created': self.created,
            'owned': self.is_owned()
        }

    def like(self):
        post_like = Like(user=current_user, post=self)

        db.session.add(post_like)
        db.session.commit()

        return post_like

    def unlike(self):
        return Like.query.filter_by(user_id=current_user.id, post_id=self.id).one()

    def is_liked(self):
        if not current_user.is_authenticated:
            return False

        return db.session.query(exists().where(and_(Like.user_id == current_user.id, Like.post_id == self.id))).scalar()

    def is_owned(self):
        if not current_user.is_authenticated:
            return False

        return current_user.id == self.user_id

    def update(self, image=None, text=None, tags=None):
        if image:
            new_image = Image.submit_image(image)
            self.image = new_image
        self.text = text or self.text
        if tags:
            tag_list = Tag.get_tag_list(tags)
            self.tags = tag_list

        db.session.commit()

    @classmethod
    def get_posts_data(cls, posts):
        return [post.get_data() for post in posts]

    @classmethod
    def submit_post(cls, user, file, text=None, created=None, tags=[]):
        image = Image.submit_image(file)
        tag_list = Tag.get_tag_list(tags)
        post = Post(image=image, user=user, text=text, tags=tag_list, created=created)

        db.session.add(post)
        db.session.commit()

        return post

class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('likes', lazy='dynamic'), uselist=False)

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    post = db.relationship('Post', backref=db.backref('likes', lazy='dynamic'), uselist=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user, post, created=None):
        self.user = user
        self.post = post
        self.created = created

    def __repr__(self):
        return '<Like {} - {}>'.format(self.user, self.post)

    def get_data(self):
        return {
            'post': self.post,
            'user': self.user.username,
            'created': self.created
        }

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

    def get_avatar(self):
        return self.avatar.image.link if self.avatar else None

    def get_user_info(self):
        return {
            'username': self.username,
            'avatar': self.get_avatar()
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

    def get_messages(self):
        return Message.query.filter(or_(Message.target_id == self.id, Message.user_id == self.id)).all()

    def set_avatar(self, file):
        image = Image.submit_image(file)
        avatar = Avatar(self, image)

        db.session.add(avatar)
        db.session.commit()

        return image

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

    def get_data(self):
        return {
            'target': self.target.username,
            'follower': self.follower.username
        }

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

    @staticmethod
    def format_tags(tags_string):
        """ Converts string of tag names to list of tag names """
        return set(t.replace(' ', '') for t in tags_string.lower().split(','))

    @classmethod
    def get_or_create_tag(cls, name):
        """ Create or find a Tag from the given tag name """
        return cls.query.filter_by(name=name).one_or_none() or cls(name)

    @classmethod
    def get_tag_list(cls, tags):
        """ Generate a list of Tag models from a list of tag names, stripping out empty tag strings """
        tag_set = cls.format_tags(tags)
        return [cls.get_or_create_tag(tag) for tag in tag_set if tag]

class OAuth(db.Model, OAuthConsumerMixin):
    __tablename__ = 'oauths'

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    target = db.relationship('User', foreign_keys='Message.target_id', backref=db.backref('messages_to', lazy='dynamic'),
                             uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', foreign_keys='Message.user_id',
                               backref=db.backref('messages_from', lazy='dynamic'), uselist=False)
    text = db.Column(db.String, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, target, user, text, created=None):
        self.target = target
        self.user = user
        self.text = text
        self.created = created

    def get_data(self):
        return {
            'from': self.user.username,
            'to': self.target.username,
            'text': self.text,
            'created': self.created
        }

    @classmethod
    def get_message_data(cls, messages):
        return [m.get_data() for m in messages]

    @classmethod
    def send_message(cls, username, text):
        target = User.query.filter_by(username=username).one_or_none()
        if not target:
            return False
        message = cls(target, current_user, text)

        db.session.add(message)
        db.session.commit()

        return message

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('comments', lazy='dynamic'), uselist=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    post = db.relationship('Post', backref=db.backref('comments', lazy='joined'), uselist=False, order_by='Comment.created')
    text = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user, post, text, created=None):
        self.user = user
        self.post = post
        self.text = text
        self.created = created

    def __repr__(self):
        return '<Comment {} {}>'.format(self.user, self.text)

    def get_data(self):
        return {
            'user': self.user.username,
            'post': self.post.id,
            'text': self.text,
            'created': self.created
        }

    @classmethod
    def send_comment(cls, post_id, text):
        post = Post.query.get(post_id)

        comment = cls(current_user, post, text)

        db.session.add(comment)
        db.session.commit()

        return comment

class Avatar(db.Model):
    __tablename__ = 'avatars'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('avatar', uselist=False), uselist=False)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    image = db.relationship('Image', backref=db.backref('avatars'), uselist=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user, image):
        self.user = user
        self.image = image

    def __repr__(self):
        return '<Avatar {}>'.format(self.user)
