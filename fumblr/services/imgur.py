from fumblr.keys import IMGUR_SECRET, IMGUR_ID
from imgurpython import ImgurClient
import os

API_URL = 'https://api.imgur.com/3/'

__client_id = IMGUR_ID
__client_secret = IMGUR_SECRET

__client = ImgurClient(__client_id, __client_secret)

def delete_image(deletehash):
    ''' Delete image with given deletehash '''
    try:
        return __client.delete_image(deletehash)
    except:
        return False

def upload_image(path):
    ''' Upload image at the given path '''
    image_path = os.path.abspath(path)
    upload = __client.upload_from_path(image_path)

    return upload

def get_image(id):
    ''' Get image data for id '''
    image_data = __client.get_image(id)

    return image_data

