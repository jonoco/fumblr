from fumblr import app
from fumblr.models import User, Post, Role, Image, Tag, Message
from fumblr.database import db
from flask import abort, url_for, redirect
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from fumblr.decorators import admin_required

class MyHomeView(AdminIndexView):
    @admin_required
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

class MyModelView(ModelView):
    def is_accessible(self):
        if not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                return abort(403)
            else:
                return redirect(url_for('login'))

admin = Admin(app,
              name='fumblr',
              template_mode='bootstrap3',
              index_view=MyHomeView())

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Post, db.session))
admin.add_view(MyModelView(Role, db.session))
admin.add_view(MyModelView(Image, db.session))
admin.add_view(MyModelView(Tag, db.session))
admin.add_view(MyModelView(Message, db.session))
