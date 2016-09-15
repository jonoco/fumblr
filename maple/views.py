import os
from flask import render_template, redirect, url_for, flash, request, send_from_directory
from maple import app
from flask_login import login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from .services.posts import allowed_file, create_post
from .models import Post, User
from .services.imgur import get_image

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out')
    return redirect(url_for('index'))

@app.route('/upload', methods=['get', 'post'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template('upload.html')

    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file not in request')
        return redirect(url_for('post'))

    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('post'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        text = request.form['text']
        post = create_post(current_user, path, text)

        ## delete file after uploading it
        os.remove(path)

        return redirect(url_for('view_post', id=post.id))

@app.route('/post/<id>')
def view_post(id):
    post = Post.query.get(id)
    post_data = {
        'link': post.image.link,
        'text': post.text or '',
        'user': post.user.username
    }


    return render_template('post.html', post=post_data)

@app.route('/gallery')
def gallery():
    posts = Post.query.limit(10).all()
    items = [{'link': post.image.link, 'id': post.id} for post in posts]

    return render_template('gallery.html', items=items)

@app.route('/user/<username>')
def user(username):
    # TODO sanitize username input?
    user = User.query.filter_by(username=username).first()

    return ''


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')


