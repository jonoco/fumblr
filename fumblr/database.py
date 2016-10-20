from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def setup_database():
    """
    Setup some initial conditions after clearing database

    """

    from fumblr.models import Role

    role_user = Role('user', 'basic user role')
    role_superuser = Role('superuser', 'admin privileges user')

    db.session.add(role_user)
    db.session.add(role_superuser)
    db.session.commit()

    print('User and Superuser roles created')