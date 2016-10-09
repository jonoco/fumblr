from fumblr.keys import IMGUR_SECRET, IMGUR_ID
from imgurpython import ImgurClient, helpers
import os

API_URL = 'https://api.imgur.com/3/'

__client_id = IMGUR_ID
__client_secret = IMGUR_SECRET

try:
    __client = ImgurClient(__client_id, __client_secret)
except helpers.error.ImgurClientError:
    print('Error: imgur client error')
    __client = None

def delete_image(deletehash):
    """
    Delete image from Imgur with given deletehash

    Args:
        deletehash: Hash id of image to delete

    Returns:
        Response from Imgur of image deletion if successful, otherwise False
    """
    try:
        return __client.delete_image(deletehash)
    except:
        return False

def upload_image(path):
    """
    Upload image at system path to Imgur

    Example of response data from Imgur upload:

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

    Args:
        path: System path of image

    Returns:
        Response from Imgur

    """
    image_path = os.path.abspath(path)
    upload = __client.upload_from_path(image_path)

    return upload

def get_image(id):
    """
    Return image data for image with given id

    Args:
        id: Imgur image id

    Returns:
        Response from Imgur
    """
    image_data = __client.get_image(id)

    return image_data

