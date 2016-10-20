from functools import wraps
from flask import redirect, url_for, request
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))

        if current_user.has_role('superuser'):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('index'))

    return decorated_function
