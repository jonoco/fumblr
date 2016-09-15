from .imgur import upload_image
from maple.models import User, Post, Image
from maple.database import db

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def create_post(user, image_path, text=None, created=None):
    """
    creates and store a post object from a user and image

    :param username:
    :param image_path:
    :return Post:
    """

    image = create_image(image_path)
    post = Post(image, user, text, created)

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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS




