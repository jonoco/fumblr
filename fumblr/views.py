from flask import render_template, redirect, url_for, flash, request, jsonify, current_app, json
from fumblr import app
from flask_login import login_required, logout_user, current_user, user_needs_refresh
from .models import Post, User, Image, Tag, Follow, Like
from .database import db

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
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

@app.route('/settings', methods=['get', 'post'])
@login_required
def settings():
    if request.method == 'GET':
        return render_template('settings.html', user=current_user.get_user_info(), error={})

    new_username = request.form['username']
    if User.username_taken(new_username):
        error = {
            'username': '{} is already taken'.format(new_username)
        }
        return render_template('settings.html', user=current_user.get_user_info(), error=error)
    else:
        user = current_user
        user.username = new_username
        db.session.commit()

    #refresh login manager
    user_needs_refresh.send(current_app._get_current_object())

    return render_template('settings.html', user=current_user.get_user_info(), error={})

@app.route('/post', methods=['post'])
@login_required
def new_post():
    file = request.files['file']
    if file and Image.allowed_file(file.filename):

        tags_string = request.form['tags']
        tags = Tag.format_tags_string(tags_string)
        text = request.form['text']

        post = Post.submit_post(current_user, file, text, tags=tags)

        return jsonify(redirect=url_for('view_post', id=post.id))

@app.route('/post/<id>')
def view_post(id):
    post = Post.query.get(id)
    if not post:
        return redirect(url_for('index'))

    post_data = post.get_data()

    return render_template('view_post.html', post=post_data)

@app.route('/post/delete/<id>')
@login_required
def delete_post(id):
    post = current_user.posts.filter_by(id=id).one_or_none()
    if not post:
        return ('Cannot delete, post does not belong to user', 403)

    db.session.delete(post)
    db.session.commit()

    return ('Post deleted', 204)

@app.route('/post/edit/<id>', methods=['get', 'post'])
@login_required
def edit_post(id):
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

    tags = Tag.format_tags_string(request.form.get('tags'))
    file = request.files.get('file')
    post.update(text=request.form.get('text'), tags=tags, image=file)

    return jsonify(reload=True)

@app.route('/gallery')
@app.route('/gallery/<int:page>')
def gallery(page=0):
    PAGE_LIMIT = 20

    posts = Post.query.order_by(Post.created.desc()).offset(page).limit(PAGE_LIMIT).all()
    posts_data = Post.get_posts_data(posts)

    total_count = Post.query.count()
    offset = len(posts_data) + page
    more_posts = total_count > offset

    return render_template('gallery.html', posts=posts_data, more_posts=more_posts, offset=offset)

@app.route('/dashboard')
@login_required
def dashboard():
    following_ids = current_user.following.with_entities(Follow.target_id).all()
    following_ids.append(current_user.id)

    posts = Post.query.filter(Post.user_id.in_(following_ids)).order_by(Post.created.desc()).all()
    posts_data = Post.get_posts_data(posts)

    return render_template('dashboard.html', posts=posts_data)

@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    posts = user.posts.order_by(Post.created.desc())
    posts_data = Post.get_posts_data(posts)

    if current_user.is_authenticated:
        is_following = current_user.following_user(username)
    else:
        is_following = False

    return render_template('blog.html', posts=posts_data, user=username, is_following=is_following)

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

    if username == current_user.username:
        flash('Cannot follow yourself')
        return ('', 403)

    is_following = current_user.following_user(username)

    if is_following:
        current_user.stop_following_user(username)
    else:
        current_user.follow_user(username)

    return jsonify(following=is_following)

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

    return jsonify(like=liked)

@app.route('/search')
def search():
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
    tag = Tag.query.filter_by(name=tag_name).first()
    if not tag:
        return render_template('search.html', no_results=True)

    posts = tag.posts.order_by(Post.created.desc())

    posts_data = Post.get_posts_data(posts)

    return render_template('search.html', tag=tag_name, posts=posts_data)

@app.route('/following')
@login_required
def following():
    followings = current_user.following
    following_data = [f.get_data() for f in followings]

    return render_template('following.html', following=following_data)

@app.route('/followers')
@login_required
def followers():
    followers_query = current_user.followers
    followers_data = [f.get_data() for f in followers_query]

    return render_template('followers.html', followers=followers_data)

@app.route('/likes')
@login_required
def likes():
    likes_query = current_user.likes.order_by(Like.created.desc())
    posts_data = [l.post.get_data() for l in likes_query]

    return render_template('likes.html', posts=posts_data)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('not_found.html')


