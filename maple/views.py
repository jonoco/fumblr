import os
from flask import render_template, redirect, url_for, flash, request, jsonify
from maple import app
from flask_login import login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from .services.posts import allowed_file, create_post, like_post, get_post_like, get_posts_data, get_post_data
from .models import Post, User, Image
from .database import db

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user', username=current_user.username))
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

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
        return redirect(url_for('upload'))

    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('upload'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)

        tags_string = request.form['tags']
        tags = [s.strip().lower() for s in tags_string.split(',')]
        text = request.form['text']

        post = create_post(current_user, image_path, text, tags=tags)

        ## delete image after uploading it
        os.remove(image_path)

        return redirect(url_for('view_post', id=post.id))

@app.route('/settings', methods=['get', 'post'])
@login_required
def settings():
    if request.method == 'GET':
        return render_template('settings.html')

    #TODO get new user settings and update user info

    return render_template('settings.html')

@app.route('/post/<id>')
def view_post(id):
    post = Post.query.get(id)
    post_data = get_post_data(post)

    return render_template('view_post.html', post=post_data)

@app.route('/gallery')
def gallery():
    posts = Post.query.order_by(Post.created).limit(20).all()
    posts_data = get_posts_data(posts)

    return render_template('gallery.html', posts=posts_data)

@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    posts = user.posts
    posts_data = get_posts_data(posts)

    return render_template('blog.html', posts=posts_data, user=username)

@app.route('/image/<id>')
def get_image(id):
    # route for checking image properties
    image = Image.query.get(id)
    image_data = {
        'link': image.link,
        'created': image.created
    }

    return render_template('image.html', image=image_data)

@app.route('/follow', methods=['post'])
@login_required
def follow():
    """
        Follow a user
    """

    req = request.get_json()
    username = req['user']
    following = current_user.following_user(username)

    if following:
        current_user.stop_following_user(username)
    else:
        current_user.follow_user(username)

    return jsonify(following=following)

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

@app.route('/search')
def search():
    q = request.args.get('q')
    query = '%{}%'.format(q)

    users = User.query.filter(User.username.like(query)).all()
    posts = Post.query.filter(Post.text.like(query)).all()

    users_data = [user.get_user_info() for user in users]
    posts_data = get_posts_data(posts)

    return render_template('search.html', posts=posts_data, users=users_data)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')


