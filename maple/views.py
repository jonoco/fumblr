import json
import os
from flask import render_template, redirect, url_for, flash, request, jsonify
from maple import app
from flask_login import login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from .services.posts import allowed_file, create_post, like_post, get_post_like
from .models import Post, User, Image
from .database import db

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user', username=current_user.username))
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
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)
        text = request.form['text']
        post = create_post(current_user, image_path, text)

        ## delete file after uploading it
        os.remove(image_path)

        return redirect(url_for('view_post', id=post.id))

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/post/<id>')
def view_post(id):
    post = Post.query.get(id)

    likes = [{
        'user': l.user.username
    } for l in post.likes]

    liked = False
    for like in likes:
        if current_user.username == like['user']:
            liked = True

    post_data = {
        'id': post.id,
        'link': post.image.link,
        'text': post.text or '',
        'user': post.user.username,
        'likes': likes,
        'liked': liked
    }

    return render_template('post.html', post=post_data)

@app.route('/gallery')
def gallery():
    posts = Post.query.limit(10).all()
    posts_data = [{
                      'id': post.id,
                      'link': post.image.link,
                      'text': post.text or '',
                      'user': post.user.username
                  } for post in posts]

    return render_template('gallery.html', posts=posts_data)

@app.route('/user/<username>')
def user(username):
    # TODO sanitize username input?
    user = User.query.filter_by(username=username).first()
    posts = user.posts
    posts_data = [{
                      'id': post.id,
                      'link': post.image.link,
                      'text': post.text or '',
                      'user': post.user.username
                  } for post in posts]


    return render_template('blog.html', posts=posts_data)

@app.route('/image/<id>')
def get_image(id):
    # route for checking image properties
    image = Image.query.get(id)
    image_data = {
        'link': image.link,
        'created': image.created
    }

    return render_template('image.html', image=image_data)

@app.route('/like', methods=['post'])
@login_required
def like():
    """
        Like a post by posting the post's id
        request['post'] = post_id
    """

    req = request.get_json()
    post_id = int(req['post'])

    liked = get_post_like(post_id)
    if liked:
        db.session.delete(liked)
        db.session.commit()
        like = False
    else:
        like_post(post_id)
        like = True

    return jsonify(like=like)

## debugging/testing routes

@app.route('/test')
def test():
    thing = request.args.get('thing', type=str)

    msg = thing * 3
    return jsonify(result=msg)

@app.route('/testpost', methods=['post'])
def testpost():
    for a in request.args:
        print('args - {}'.format(a))
    for f in request.form:
        print('form - {}'.format(f))

    print('json - {}'.format(request.get_json()))


    return jsonify(result='post success?')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')


