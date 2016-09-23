from .imgur import upload_image
from ..models import User, Post, Image, Like, Tag
from ..database import db
from flask_login import current_user

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def create_post(user, image_path, text=None, created=None, tags=[]):
    """
    creates and store a post object from a user and image

    :param username:
    :param image_path:
    :return Post:
    """

    image = create_image(image_path)
    tag_list = Tag.get_tag_list(tags)
    post = Post(image=image, user=user, text=text, tags=tag_list, created=created)

    db.session.add(post)
    db.session.commit()

    return post

def create_image(image_path):
    """
    upload and save image to database

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


    :param image_path:
    :return Image:
    """

    image_data = upload_image(image_path)
    image = Image(image_data['id'], image_data['deletehash'], image_data['link'])

    db.session.add(image)
    db.session.commit()

    return image

#DEPRECATED
def like_post(post_id):
    """ create a like for a post """
    post = Post.query.get(post_id)
    like = Like(user=current_user, post=post)

    db.session.add(like)
    db.session.commit()

    return like

#DEPRECATED
def get_post_like(post_id):
    """ return like of post liked by user """
    if not current_user.is_authenticated:
        return False

    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    return like

#DEPRECATED - use Post method
def get_post_data(post):
    if current_user.is_authenticated:
        user = current_user.username
    else:
        user = ''

    return {
            'id': post.id,
            'link': post.image.link,
            'text': post.text or '',
            'user': post.user.username,
            'likes': post.likes.count(),
            'liked': any(l.user.username == user for l in post.likes),
            'tags': [tag.name for tag in post.tags],
            'created': post.created
        }

#DEPRECATED - use Post method
def get_posts_data(posts):
    """ Strips post data off of array of Posts """
    return [get_post_data(post) for post in posts]

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS




