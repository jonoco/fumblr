from fumblr.keys import IMGUR_SECRET, IMGUR_ID
from imgurpython import ImgurClient, helpers
import os
import base64

API_URL = 'https://api.imgur.com/3/'

def get_client():
    """
    Get an API client for Imgur

    Returns:
        Imgur client if it is available

    """
    try:
        return ImgurClient(IMGUR_ID, IMGUR_SECRET)
    except helpers.error.ImgurClientError:
        print(f'Error: imgur client error - id: {IMGUR_ID} secret: {IMGUR_SECRET}')

def delete_image(deletehash):
    """
    Delete image from Imgur with given deletehash

    Args:
        deletehash: Hash id of image to delete

    Returns:
        Response from Imgur of image deletion if successful, otherwise False
    """

    client = get_client()
    if client:
        try:
            return client.delete_image(deletehash)
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

    client = get_client()
    if client:
        image_path = os.path.abspath(path)
        upload = client.upload_from_path(image_path)

        return upload

def upload(image):
    """
    Upload image to Imgur from file

    Args:
        image: File object

    Returns:
        Imgur response object

    """

    client = get_client()
    if client:
        contents = image.read()
        b64 = base64.b64encode(contents)
        data = {
            'image': b64,
            'type': 'base64'
        }
        return client.make_request('POST', 'upload', data, True)


def upload_from_url(url):
    """
    Upload image to Imgur from url

    Args:
        url: URL of image

    Returns:
        Imgur Response object if successful, otherwise False

    """
    client = get_client()
    if client:
        try:
            return client.upload_from_url(url)
        except helpers.error.ImgurClientError:
            print('Error: imgur client error')
            return False

def get_image(id):
    """
    Return image data for image with given id

    Args:
        id: Imgur image id

    Returns:
        Response from Imgur

    """

    client = get_client()
    if client:
        image_data = client.get_image(id)

        return image_data

