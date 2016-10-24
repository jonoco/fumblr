#!/usr/bin/env python

import sys
import os
from fumblr import app
from fumblr.database import db, setup_database

if __name__ == '__main__':
    if '--drop' in sys.argv:
        with app.app_context():
            db.drop_all()
            db.session.commit()
            print('Database tables dropped')

    if '--clear' in sys.argv:
        with app.app_context():
            db.reflect()
            db.drop_all()
            db.create_all()
            setup_database()
            db.session.commit()
            print('Database tables dropped and recreated')

    if '--setup' in sys.argv:
        with app.app_context():
            db.create_all()
            db.session.commit()
            print('Database tables created')

    else:
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        app.run(host=host, port=port)