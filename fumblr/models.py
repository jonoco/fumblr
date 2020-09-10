from flask import current_app
from .database import db
from .services.imgur import upload, upload_from_url
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin
from flask_login import UserMixin, current_user, login_user, logout_user
from datetime import datetime
from sqlalchemy import exists, and_, or_
from werkzeug.utils import secure_filename
from passlib.hash import sha256_crypt
import os
import re
import random

tags_posts = db.Table('tag_post_association',
                      db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
                      db.Column('post_id', db.Integer, db.ForeignKey('posts.id')))

images_posts = db.Table('image_post_association',
                        db.Column('image_id', db.Integer, db.ForeignKey('images.id')),
                        db.Column('post_id', db.Integer, db.ForeignKey('posts.id')))

roles_users = db.Table('role_user_association',
                       db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                       db.Column('role_id', db.Integer, db.ForeignKey('roles.id')))

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(80), nullable=False)
    link = db.Column(db.String(80), nullable=False)
    deletehash = db.Column(db.String(80), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, image, deletehash, link, created=None):
        self.image = image
        self.deletehash = deletehash
        self.link = link
        self.created = created

    def __repr__(self):
        return '<Image {} {}>'.format(self.id, self.image)

    def get_data(self):
        return {
            'id': self.id,
            'link': self.link,
            'created': self.created
        }

    @staticmethod
    def allowed_file(filename):
        """
        Returns True if filename uses one of the permitted file extensions, otherwise False

        """

        ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    @classmethod
    def submit_images(cls, files):
        """
        Upload multiple images to Imgur

        Args:
            files: List of File objects containing single images

        Returns:
            List of new Image objects

        """

        images = []

        for f in files:
            image_data = upload(f)

            if not image_data:
                raise Exception('submit_images: No upload data received')

            image = cls(image_data['id'], image_data['deletehash'], image_data['link'])
            images.append(image)
            db.session.add(image)

        db.session.commit()

        return images

    @classmethod
    def submit_image(cls, file):
        """
        Upload image to Imgur

        Args:
            file: File object containing image

        Returns:
            New Image object

        """

        image_data = upload(file)
        image = Image(image_data['id'], image_data['deletehash'], image_data['link'])

        db.session.add(image)
        db.session.commit()

        return image

    @classmethod
    def submit_image_url(cls, url):
        """
        Upload image to Imgur from url

        Args:
            url: URL to image

        Returns:
            New Image object

        """

        image_data = upload_from_url(url)
        if not image_data:
            return False

        image = Image(image_data['id'], image_data['deletehash'], image_data['link'])

        db.session.add(image)
        db.session.commit()

        return image

    @classmethod
    def save_image(cls, file):
        """
        Save image to file system

        Args:
            file: File object containing image

        Returns:
            System path to saved image file

        """
        filename = secure_filename(file.filename)
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        file.save(image_path)

        return image_path

    @classmethod
    def delete_image(cls, file):
        """
        Delete image from file system

        Args:
            file: File object containing image

        """
        filename = secure_filename(file.filename)
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        os.remove(image_path)

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', foreign_keys='Post.user_id', backref=db.backref('posts', lazy='dynamic'), uselist=False)

    images = db.relationship('Image', secondary=images_posts, backref=db.backref('posts'))
    tags = db.relationship('Tag', secondary=tags_posts, backref=db.backref('posts', lazy='dynamic'))

    reblog_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reblog_user = db.relationship('User', foreign_keys='Post.reblog_user_id', uselist=False)

    reblog_post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    reblogs = db.relationship('Post', backref=db.backref('reblog_parent', uselist=False, remote_side=[id]), uselist=True)

    updated = db.Column(db.DateTime, default=datetime.utcnow)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, images, user, tags=None, text=None, created=None):
        self.images = images
        self.user = user
        self.text = text
        self.tags = tags
        self.created = created

    def __repr__(self):
        return '<Post {} {}>'.format(self.id, self.user)

    def get_data(self):
        return {
            'id': self.id,
            'images': [i.get_data() for i in self.images],
            'text': self.text or '',
            'user': self.user.get_user_info(),
            'likes': [l.get_data() for l in self.likes],
            'liked': self.is_liked(),
            'tags': [tag.name for tag in self.tags],
            'comments': [cmt.get_data() for cmt in self.comments],
            'created': self.created,
            'owned': self.is_owned(),
            'reblogs': [r.id for r in self.reblogs],
            'reblog': self.reblog_user.get_user_info() if self.reblog_user else None
        }

    def reblog_post(self, tags=[], text=None):
        """
        Create and return a reblog post

        Args:
            tags: String of tags, separated by commas
            text: String description of post

        Returns:
            New Post object with reblog properties

        """
        reblog = Post(self.images, current_user, Tag.get_tag_list(tags), text)
        self.reblogs.append(reblog)
        reblog.reblog_user = self.user

        db.session.add(reblog)
        db.session.commit()

        return reblog

    def like(self):
        """
        Create a new Like object for post

        Returns:
            New Like object

        """
        post_like = Like(user=current_user, post=self)

        db.session.add(post_like)
        db.session.commit()

        return post_like

    def unlike(self):
        """
        Delete user's Like object from post

        """
        like = Like.query.filter_by(user_id=current_user.id, post_id=self.id).one()

        db.session.delete(like)
        db.session.commit()

    def is_liked(self):
        """
        Returns True if current user liked post, otherwise False

        """
        if not current_user.is_authenticated:
            return False

        return db.session.query(exists().where(and_(Like.user_id == current_user.id, Like.post_id == self.id))).scalar()

    def is_owned(self):
        """
        Returns True if post belongs to current user, otherwise False

        """
        if not current_user.is_authenticated:
            return False

        return current_user.id == self.user_id

    def update(self, images=None, text=None, tags=None):
        """
        Update a post's image, text, or tags

        Args:
            images: List of Images objects
            text: Description of post
            tags: String of tags, separated by comma

        """

        if images:
            self.images = images

        if text:
            self.text = text

        if tags:
            self.tags = Tag.get_tag_list(tags)

        self.updated = datetime.utcnow()
        db.session.commit()

    @classmethod
    def get_posts_data(cls, posts):
        """
        Returns list of post data

        """
        return [post.get_data() for post in posts]

    @classmethod
    def submit_post(cls, user, images, text=None, tags='', created=None):
        """
        Create a new post and save it to the database

        Args:
            user: User object of user posting post
            images: List of Image objects
            text: Description of post
            created: Datetime when post created
            tags: String of tags, separated by comma

        Returns:
            New Post object

        """

        tag_list = Tag.get_tag_list(tags)
        post = Post(images=images, user=user, text=text, tags=tag_list, created=created)

        db.session.add(post)
        db.session.commit()

        return post

class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('likes', lazy='dynamic'), uselist=False)

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
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
    loginname = db.Column(db.String, nullable=False)
    provider = db.Column(db.String)
    avatar_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    avatar = db.relationship('Image', backref=db.backref('avatars', lazy='dynamic'), uselist=False)

    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)

    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, loginname, provider, created=None):

        self.loginname = loginname
        self.provider = provider
        self.username = User.generate_username(loginname)
        self.created = created

    def __repr__(self):
        return '<User {} {}>'.format(self.id, self.username)

    @classmethod
    def valid_username(cls, username):
        """
        Check if username contains illegal characters

        """
        ALLOWED_CHARACTERS = re.compile('[a-zA-Z0-9-_]+')
        return ALLOWED_CHARACTERS.match(username)

    @classmethod
    def username_taken(cls, username):
        """
        Check if given username already exists in the database

        """
        return db.session.query(exists().where(User.username == username)).scalar()

    @classmethod
    def generate_username(cls, loginname):
        """
        Generates a username for a user

        Args:
            loginname: Name provided by oauth provider

        Returns:
            A unique username

        """
        if cls.username_taken(loginname):
            rand_num = random.randrange(100, 999)
            return '{}{}'.format(loginname, rand_num)
        else:
            return loginname

    @classmethod
    def valid_email(cls, email):
        """
        Check if email conforms to a valid email pattern

        """
        email_pattern = re.compile('^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$')
        return email_pattern.match(email)

    @classmethod
    def email_taken(cls, email):
        """
        Check if given email already exists in database

        """

        return db.session.query(exists().where(User.email == email)).scalar()

    @classmethod
    def valid_password(cls, password):
        """
        Check if password conform to a valid password pattern

        Example:
            Password between 8 and 20 characters including any @*#$%^&* characters

        """
        password_pattern = re.compile('^([a-zA-Z0-9@*#$%^&]{8,20})$')
        return password_pattern.match(password)

    def get_user_info(self):
        return {
            'username': self.username,
            'avatar': self.get_avatar()
        }

    def following_user(self, username):
        """
        Check if current user is following given user

        """
        return any(username == f.target.username for f in self.following)

    def follow_user(self, username):
        """
        Follow user of given username and returns new Follow object

        """

        user = User.query.filter_by(username=username).first()
        follow = Follow(target_user=user, follower_user=self)

        db.session.add(follow)
        db.session.commit()

        return follow

    def stop_following_user(self, username):
        """
        Stop following given user by deleting relevant Follow object

        Returns:
            True if the current user was following the user, otherwise False

        """
        follow = next(f for f in self.following if f.target.username == username)
        if follow:
            db.session.delete(follow)
            db.session.commit()
            return True
        else:
            return False

    def get_messages(self):
        """
        Retrieves all message sent to or from user

        Returns:
            List of Message objects

        """
        return Message.query.filter(or_(Message.target_id == self.id, Message.user_id == self.id)).all()

    def get_avatar(self):
        """
        Retrieves user's avatar image if it exists

        Returns:
            Avatar's image link if it exists, otherwise None

        """
        return self.avatar.link if self.avatar else None

    def set_avatar(self, file):
        """
        Set a new user avatar, saving the new avatar image

        Args:
            file: object containing image

        Returns:
            Image object of the avatar

        """
        image = Image.submit_image(file)
        self.avatar = image

        db.session.commit()

        return image

    def has_role(self, name):
        for role in self.roles:
            if role.name == name:
                return True

        return False

    @staticmethod
    def hash_password(pw):
        """
        Hash and return a given password

        Args:
            pw: Password to hash

        Returns:
            Hash string

        """

        return sha256_crypt.encrypt(pw)

    def verify_password(self, pw):
        """
        Verifies given password matches user's hashed password

        Args:
            pw: Password to compare against user's password

        Returns:
            Returns True if passwords match, otherwise False

        """
        if not self.password:
            return False

        return sha256_crypt.verify(pw, self.password)

    def login(self):
        """
        Register user as logged in

        """
        login_user(self)
        self.login_count = self.login_count + 1
        self.last_login_at = self.current_login_at
        self.current_login_at = datetime.utcnow()

        db.session.commit()

    def logout(self):
        """
        Unregister user as logged in

        """
        logout_user()

class Follow(db.Model):
    __tablename__ = 'followers'

    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target = db.relationship('User', foreign_keys='Follow.target_id', backref=db.backref('followers', lazy='dynamic'), uselist=False)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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
    name = db.Column(db.String, unique=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, created=None):
        self.name = name
        self.created = created

    def __repr__(self):
        return '<Tag - {}>'.format(self.name)

    @staticmethod
    def safe_tag(tag_string):
        """
        Check if tag contains only allowed characters

        Args:
            tag_string: String of tag

        Returns:
            Returns True if string contains only allowed characters, otherwise False

        """
        ALLOWED_CHARACTERS = re.compile('[a-zA-Z0-9,!?+\- ]+')
        return ALLOWED_CHARACTERS.match(tag_string)

    @staticmethod
    def format_tags(tags):
        """
        Convert and format a string of tag names to a set.

        Example:
            'comedy, tragedy, romantic tragedy' -> set(comedy, tragedy, romantic tragedy)

        Args:
            tags: A string of tag names, separated by commas.

        Returns:
            A set of tag name strings.

        """
        return set(' '.join(t.split()) for t in tags.lower().split(','))

    @classmethod
    def get_or_create_tag(cls, name):
        """
        Create or find a Tag from the given tag name and return the Tag.

        """
        return cls.query.filter_by(name=name).one_or_none() or cls(name)

    @classmethod
    def get_tag_list(cls, tags):
        """
        Return a list of Tags from a tag string.

        Args:
            tags: A string of tan names, separated by commas.

        Returns:
            A list of Tag objects.

        """
        if not tags:
            return []
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
    target_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target = db.relationship('User', foreign_keys='Message.target_id', backref=db.backref('messages_to', lazy='dynamic'),
                             uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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
            'read': self.read,
            'created': self.created
        }

    @classmethod
    def get_message_data(cls, messages):
        return [m.get_data() for m in messages]

    @classmethod
    def send_message(cls, username, text):
        """
        Create new Message

        Args:
            username: Recipient of new message
            text: Message body

        Returns:
            New Message object

        """
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy='dynamic'), uselist=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
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
            'id': self.id,
            'user': self.user.username,
            'post': self.post.id,
            'text': self.text,
            'created': self.created
        }

    @classmethod
    def send_comment(cls, post_id, text):
        """
        Create new Comment object

        Args:
            post_id: ID of post to comment upon
            text: Body of comment

        Returns:
            New Comment object

        """
        post = Post.query.get(post_id)

        comment = cls(current_user, post, text)

        db.session.add(comment)
        db.session.commit()

        return comment

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Role {} {}>'.format(self.id, self.name)

    @classmethod
    def get_role(cls, name):
        """
        Create or find a Role from the given role name and return the Role.

        """
        return cls.query.filter_by(name=name).one_or_none() or cls(name)