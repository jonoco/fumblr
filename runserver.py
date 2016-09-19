import sys
import os
from maple import app
from maple.database import db

if __name__ == '__main__':
    if '--setup' in sys.argv:
        with app.app_context():
            db.create_all()
            db.session.commit()
            print('Database tables created')
    else:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        app.run()