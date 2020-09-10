from flask import render_template, redirect, url_for, flash, request, jsonify, current_app, json, abort
from fumblr import app
from flask_login import login_required, logout_user, current_user, user_needs_refresh
from .models import Post, User, Image, Tag, Follow, Like, Message, Comment, Role
from .database import db
from .default_settings import DEBUG
import os

POST_LIMIT = 10

@app.route('/')
def index():
    """
        Home page
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/login', methods=['get', 'post'])
def login():
    """
        Log in page
    """
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email')
    password = request.form.get('password')
    error = None
    user = User.query.filter_by(email=email).one_or_none()
    if not user:
        error = 'No user found with that email'

    if user and not user.verify_password(password):
        error = 'Password invalid'

    if error:
        return render_template('login.html', error=error)

    user.login()
    flash('Logged in successfully')
    return redirect(url_for('dashboard'))

@app.route('/register', methods=['get', 'post'])
def register():
    """
    Registration page

    """
    if request.method == 'GET':
        return render_template('register.html')

    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')

    if User.username_taken(username):
        return render_template('register.html', error='Username taken')

    if User.email_taken(email):
        return render_template('register.html', error='Email taken')

    if not User.valid_username(username):
        return render_template('register.html', error='Invalid username')

    if not User.valid_email(email):
        return render_template('register.html', error='Invalid email')

    if not User.valid_password(password):
        return render_template('register.html', error='Invalid password')

    user = User(email, 'email')
    user.password = User.hash_password(password)
    user.email = email
    user.username = username

    role = Role.get_role('user')
    user.roles.append(role)

    db.session.add(user)
    db.session.commit()

    user.login()

    flash('Registered successfully')

    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    """
        Log out
    """
    logout_user()
    flash('You have logged out')
    return redirect(url_for('index'))

@app.route('/valid/username/<username>')
@app.route('/valid/email/<email>')
def valid(username=None, email=None):
    if username:
        if User.username_taken(username):
            return ('Username taken', 418)
        else:
            return ('Username available', 204)

    if email:
        if User.email_taken(email):
            return ('Email taken', 418)
        else:
            return ('Email available', 204)

    return abort(404)

@app.route('/settings')
@login_required
def settings():
    """
        User's account settings
    """
    return render_template('settings.html')

@app.route('/settings/username', methods=['post'])
@login_required
def set_username():
    """
        Set a user's username
    """
    new_username = request.form['username']

    if not new_username:
        return render_template('settings.html', error={'username': 'Please enter a username'})

    if User.username_taken(new_username):
        return render_template('settings.html', error={'password': 'Username taken'})

    current_user.username = new_username
    db.session.commit()

    user_needs_refresh.send(current_app._get_current_object())
    flash('Updated username to {}'.format(new_username))
    return render_template('settings.html')

@app.route('/settings/password', methods=['post'])
@login_required
def set_password():
    """
    Set a new password

    """
    orig_password = request.form.get('original-password')
    new_password = request.form.get('new-password')

    if not orig_password or not new_password:
        return render_template('settings.html', error={'password': 'Please enter your password and new password'})

    if not User.valid_password(new_password):
        return render_template('settings.html', error={'password': 'Invalid password'})

    if not current_user.verify_password(orig_password):
        return render_template('settings.html', error={'password': 'Incorrect password'})

    current_user.password = User.hash_password(new_password)
    db.session.commit()

    user_needs_refresh.send(current_app._get_current_object())
    flash('Updated password')
    return render_template('settings.html')

@app.route('/settings/avatar', methods=['post'])
@login_required
def set_avatar():
    """
        Set a user avatar
    """
    file = request.files['file']

    if not file or not Image.allowed_file(file.filename):
        return render_template('settings.html', error={'avatar': 'Invalid image'})

    current_user.set_avatar(file)
    user_needs_refresh.send(current_app._get_current_object())
    return render_template('settings.html')

@app.route('/message', methods=['get'])
@app.route('/message/user/<username>', methods=['post'])
@login_required
def message(username=None):
    """
        Get and send messages
    """
    if request.method == 'GET':
        messages = current_user.get_messages()
        message_data = Message.get_message_data(messages)

        users = set()
        for u in message_data:
            users.add(u['from'])
            users.add(u['to'])

        user_messages = {u: [m for m in message_data
                             if m['from'] == u and m['to'] == current_user.username
                             or m['to'] == u and m['from'] == current_user.username]
                         for u in users if u != current_user.username}

        # print(json.dumps(user_messages, indent=4, sort_keys=True))

        return render_template('messages.html', users=user_messages)

    if username:
        if not User.username_taken(username):
            return ('No user with that username', 403)
        req = request.get_json()
        text = req['text']
        msg = Message.send_message(username, text)

        return jsonify(message=render_template('component/message.html', message=msg.get_data()), user=username)

@app.route('/comment/post/<post_id>', methods=['post'])
@app.route('/comment/delete/<delete_id>', methods=['post'])
@login_required
def comment(post_id=None, delete_id=None):
    """
    Create or delete comment on a post

    """
    if post_id:
        req = request.get_json()
        text = req.get('text')

        cmt = Comment.send_comment(post_id, text)

        return jsonify(comment=cmt.get_data())

    if delete_id:
        cmt = current_user.comments.filter_by(id=delete_id).one_or_none()
        if not cmt:
            return abort(404)

        db.session.delete(cmt)
        db.session.commit()

        return jsonify(comment=True)

    return abort(404)

@app.route('/reblog/<int:post_id>', methods=['get', 'post'])
@login_required
def reblog_post(post_id):
    """
    Reblog a post

    """
    if request.method == 'GET':
        post = Post.query.get(post_id)
        if not post:
            return abort(404)
        post_json = json.dumps(post.get_data())

        return jsonify(post=post_json)

    text = request.form['text']
    tags = request.form['tags']

    post = Post.query.get(post_id)
    if not post:
        return abort(404)
    if post.user_id == current_user.id:
        return abort(403)

    reblog = post.reblog_post(tags, text)
    return redirect(url_for('view_post', id=reblog.id))

@app.route('/post', methods=['post'])
@login_required
def new_post():
    """
    Create a new post

    """

    tags = request.form.get('tags')
    if tags and not Tag.safe_tag(tags):
        return ('Tag contains illegal characters', 403)

    text = request.form.get('text')

    images = []

    files = [request.files.get(f) for f in request.files]

    try:
        submitted_images = Image.submit_images(files)
    except:
        return abort(500)

    images.extend(submitted_images)

    image_ids = [int(request.form.get(item)) for item in request.form if 'image' in item]
    if image_ids:
        retrieved_images = Image.query.filter(Image.id.in_(image_ids)).all()
        images.extend(retrieved_images)

    post = Post.submit_post(current_user, images, text, tags)

    return jsonify(redirect=url_for('view_post', id=post.id))

@app.route('/post/<int:id>')
def view_post(id):
    """
        View a single post
    """
    post = Post.query.get(id)
    if not post:
        return abort(404)

    post_data = post.get_data()

    return render_template('view_post.html', post=post_data)

@app.route('/post/delete/<int:id>')
@login_required
def delete_post(id):
    """
        Delete a post
    """
    post = current_user.posts.filter_by(id=id).one_or_none()
    if not post:
        return ('Cannot delete, post does not belong to user', 403)

    db.session.delete(post)
    db.session.commit()

    return ('Post deleted', 204)

@app.route('/post/edit/<int:id>', methods=['get', 'post'])
@login_required
def edit_post(id):
    """
        Edit a post
    """
    if request.method == 'GET':
        post = current_user.posts.filter_by(id=id).one_or_none()
        if not post:
            return ('Cannot edit, post does not belong to user', 403)
        post_data = post.get_data()
        post_json = json.dumps(post_data)

        return jsonify(post=post_json)

    post = current_user.posts.filter_by(id=id).one_or_none()
    if not post:
        return ('Cannot edit, post does not belong to user', 403)

    files = [request.files.get(f) for f in request.files]
    images = []
    submitted_images = Image.submit_images(files)
    images.extend(submitted_images)

    image_ids = [int(request.form.get(item)) for item in request.form if 'image' in item]
    if image_ids:
        retrieved_images = Image.query.filter(Image.id.in_(image_ids)).all()
        images.extend(retrieved_images)

    tags = request.form.get('tags')
    if tags and not Tag.safe_tag(tags):
        return ('Tag contains illegal characters', 403)

    post.update(images=images, text=request.form.get('text'), tags=tags)

    return jsonify(reload=True)

@app.route('/gallery')
@app.route('/gallery/posts/<int:post_count>')
def gallery(post_count=0):
    """
        Posts of all users
    """
    raw_posts = request.args.get('raw_posts')

    posts = Post.query.order_by(Post.created.desc()).offset(post_count).limit(POST_LIMIT)
    posts_data = Post.get_posts_data(posts)

    total_count = Post.query.count()
    offset = len(posts_data) + post_count
    more_posts = total_count > offset

    state = {'pages': {'post_count': offset, 'more': more_posts, 'loading': False}}

    if raw_posts == '1':
        rendered_posts = ''.join([render_template('component/post.html', post=post) for post in posts_data])
        return jsonify(posts=rendered_posts, state=state)

    return render_template('gallery.html', posts=posts_data, state=state)

@app.route('/dashboard')
@app.route('/dashboard/posts/<int:post_count>')
@login_required
def dashboard(post_count=0):
    """
        User's private facing page
    """
    raw_posts = request.args.get('raw_posts')

    following_ids = current_user.following.with_entities(Follow.target_id).all()
    following_ids.append(current_user.id)

    posts_query = Post.query.filter(Post.user_id.in_(following_ids)).order_by(Post.created.desc()).offset(post_count).limit(POST_LIMIT)
    posts_data = Post.get_posts_data(posts_query)

    total_count = posts_query.count()
    offset = len(posts_data) + post_count
    more_posts = total_count > offset

    state = {'pages': {'post_count': offset, 'more': more_posts, 'loading': False}}

    if raw_posts == '1':
        rendered_posts = ''.join([render_template('component/post.html', post=post) for post in posts_data])
        return jsonify(posts=rendered_posts, state=state)

    return render_template('dashboard.html', posts=posts_data, state=state)

@app.route('/user/<username>')
@app.route('/user/<username>/posts/<int:post_count>')
def user(username, post_count=0):
    """
        User's public facing page; posts and reblogs
    """
    raw_posts = request.args.get('raw_posts')

    user = User.query.filter_by(username=username).one_or_none()
    if not user:
        return abort(404)

    posts_query = user.posts.order_by(Post.created.desc()).offset(post_count).limit(POST_LIMIT)
    posts_data = Post.get_posts_data(posts_query)

    if current_user.is_authenticated:
        is_following = current_user.following_user(username)
    else:
        is_following = False

    total_count = posts_query.count()
    offset = len(posts_data) + post_count
    more_posts = total_count > offset

    state = {'pages': {'post_count': offset, 'more': more_posts, 'loading': False}}

    if raw_posts == '1':
        rendered_posts = ''.join([render_template('component/post.html', post=post) for post in posts_data])
        return jsonify(posts=rendered_posts, state=state)

    return render_template('user.html', posts=posts_data, user=username, is_following=is_following, state=state)

@app.route('/image/<int:id>')
def get_image(id):
    """
        Check image properties
    """
    image = Image.query.get(id)
    if not image:
        return abort(404)

    return render_template('image.html', image=image.get_data())

@app.route('/image/url', methods=['post'])
@login_required
def upload_image_url():
    """
    Upload image from a url

    """
    url = request.get_json()['url']
    image = Image.submit_image_url(url)
    if not image:
        return ('Could not upload file', 403)

    image_data = image.get_data()

    return jsonify(image=image_data)

@app.route('/follow', methods=['post'])
@login_required
def follow():
    """
        Follow a user
    """

    req = request.get_json()
    username = req['user']

    if username == current_user.username:
        flash('Cannot follow yourself')
        return ('', 403)

    is_following = current_user.following_user(username)

    if is_following:
        current_user.stop_following_user(username)
    else:
        current_user.follow_user(username)

    return jsonify(follow=True)

@app.route('/like', methods=['post'])
@login_required
def like():
    """
        Like a post by posting the post's id
        request['post'] = post_id
    """

    req = request.get_json()
    post_id = int(req['post'])
    post = Post.query.get(post_id)

    liked = post.is_liked()
    if liked:
        post.unlike()
    else:
        post.like()

    return jsonify(like=True)

@app.route('/search')
def search():
    """
        Search users, posts, and tags
    """
    q = request.args.get('q')
    query = '%{}%'.format(q)

    #TODO get all posts with tag named like the query

    users = User.query.filter(User.username.like(query)).all()
    posts = Post.query.filter(Post.text.like(query)).all()
    tags = Tag.query.filter(Tag.name.like(query)).all()

    users_data = [user.get_user_info() for user in users]
    posts_data = Post.get_posts_data(posts)
    tags_data = [tag.name for tag in tags]

    return render_template('search.html', posts=posts_data, users=users_data, tags=tags_data, search=q)

@app.route('/tag/<tag_name>')
def tag(tag_name):
    """
        All posts with given tag
    """
    formatted_tag = tag_name.replace('_', ' ')
    tag = Tag.query.filter_by(name=formatted_tag).first()
    if not tag:
        return render_template('search.html', no_results=True)

    posts = tag.posts.order_by(Post.created.desc())

    posts_data = Post.get_posts_data(posts)

    return render_template('search.html', tag=tag_name, posts=posts_data)

@app.route('/following')
@login_required
def following():
    """
        All users the current user is following
    """
    followings = current_user.following
    following_data = [f.get_data() for f in followings]

    return render_template('following.html', following=following_data)

@app.route('/followers')
@login_required
def followers():
    """
        All users following the current user
    """
    followers_query = current_user.followers
    followers_data = [f.get_data() for f in followers_query]

    return render_template('followers.html', followers=followers_data)

@app.route('/likes')
@app.route('/likes/posts/<int:post_count>')
@login_required
def likes(post_count=0):
    """
        All posts the user liked
    """
    raw_posts = request.args.get('raw_posts')

    likes_query = current_user.likes.order_by(Like.created.desc()).offset(post_count).limit(POST_LIMIT)
    posts_data = [l.post.get_data() for l in likes_query]

    total_count = likes_query.count()
    offset = len(posts_data) + post_count
    more_posts = total_count > offset

    state = {'pages': {'post_count': offset, 'more': more_posts, 'loading': False}}

    if raw_posts == '1':
        rendered_posts = ''.join([render_template('component/post.html', post=post) for post in posts_data])
        return jsonify(posts=rendered_posts, state=state)

    return render_template('likes.html', posts=posts_data, state=state)

@app.errorhandler(404)
def page_not_found(error):
    """
        404 error page
    """
    return render_template('error/404.html')

@app.before_request
def before_request():
    if not DEBUG and not request.is_secure():
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)
