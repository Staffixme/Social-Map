from flask import render_template, request, redirect, url_for, flash, jsonify, g, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import app
from models import User, Post, Place, Comment, Notification
from forms import LoginForm, RegisterForm, PostForm, CommentForm, PlaceForm, ProfileForm
from urllib.parse import urlparse
import json
from helpers import (get_popular_places, allowed_file, save_image,
                     save_media_files, save_profile_image, save_place_image)
from datetime import datetime



# Home page route
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page
    posts_data = Post.get_all(limit=per_page, offset=offset)
    popular_places = get_popular_places(5)

    return render_template('index.html',
                           title="Главная",
                           posts=posts_data,
                           popular_places=popular_places,
                           page=page,
                           comment_form=CommentForm())


# API for loading more posts
@app.route('/api/posts')
def get_more_posts():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page
    posts_data = Post.get_all(limit=per_page, offset=offset)

    posts_json = []
    for post in posts_data:
        user = post.get_user()
        place = post.get_place()

        # Parse media files from JSON string
        media_list = []
        if post.media_files:
            try:
                media_list = json.loads(post.media_files)
            except:
                media_list = []

        posts_json.append({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'media_files': media_list,
            'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'likes_count': post.get_likes_count(),
            'comments_count': len(post.get_comments()),
            'user': {
                'id': user.id,
                'username': user.username,
                'avatar': user.avatar
            },
            'place': {
                'id': place.id,
                'name': place.name,
                'image_url': place.image_url
            },
            'is_liked': post.is_liked_by(current_user.id) if current_user.is_authenticated else False
        })

    return jsonify(posts_json)


# User profile page
@app.route('/user/<username>')
def user_profile(username):
    user = User.get_by_username(username)
    if user is None:
        abort(404)

    user_posts = user.get_posts()
    liked_places = user.get_liked_places()
    popular_places = get_popular_places(5)

    return render_template('profile.html',
                           title=f"Пользователь {username}",
                           user=user,
                           posts=user_posts,
                           liked_places=liked_places,
                           popular_places=popular_places)


# Subscriptions page
@app.route('/subscriptions')
@login_required
def subscriptions():
    subscribed_users = current_user.get_subscriptions()
    popular_places = get_popular_places(5)

    return render_template('subscriptions.html',
                           title="Подписки",
                           subscribed_users=subscribed_users,
                           popular_places=popular_places)


# Subscribe/unsubscribe actions
@app.route('/subscribe/<int:user_id>', methods=['POST'])
@login_required
def subscribe(user_id):
    user_to_subscribe = User.get_by_id(user_id)
    if user_to_subscribe is None:
        flash('Пользователь не найден.', 'danger')
        return redirect(url_for('index'))

    if user_id == current_user.id:
        flash('Вы не можете подписаться на себя.', 'warning')
    else:
        current_user.subscribe(user_id)
        flash(f'Вы подписались на {user_to_subscribe.username}.', 'success')

    return redirect(request.referrer or url_for('index'))


@app.route('/unsubscribe/<int:user_id>', methods=['POST'])
@login_required
def unsubscribe(user_id):
    user_to_unsubscribe = User.get_by_id(user_id)
    if user_to_unsubscribe is None:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('index'))

    current_user.unsubscribe(user_id)
    flash(f'Вы отписались от {user_to_unsubscribe.username}.', 'success')

    return redirect(request.referrer or url_for('index'))


# Places page
@app.route('/places')
def places():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    offset = (page - 1) * per_page

    top_places = Place.get_popular(3)
    places_data = Place.get_all(limit=per_page, offset=offset)
    popular_places = get_popular_places(5)

    return render_template('places.html',
                           title="Места",
                           top_places=top_places,
                           places=places_data,
                           popular_places=popular_places,
                           page=page)


@app.route('/api/places')
def get_more_places():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    offset = (page - 1) * per_page
    places_data = Place.get_all(limit=per_page, offset=offset)

    places_json = []
    for place in places_data:
        user = place.get_user()
        places_json.append({
            'id': place.id,
            'name': place.name,
            'description': place.description,
            'address': place.address,
            'latitude': place.latitude,
            'longitude': place.longitude,
            'image_url': place.image_url,
            'created_at': place.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'likes_count': place.get_likes_count(),
            'comments_count': len(place.get_comments()),
            'user': {
                'id': user.id,
                'username': user.username,
                'avatar': user.avatar
            },
            'is_liked': place.is_liked_by(current_user.id) if current_user.is_authenticated else False
        })

    return jsonify(places_json)


@app.route('/place/<int:place_id>')
def place(place_id):
    place = Place.get_by_id(place_id)
    if place is None:
        abort(404)

    place_posts = place.get_posts()
    place_comments = place.get_comments()
    comment_form = CommentForm()
    popular_places = get_popular_places(5)

    return render_template('place.html',
                           title=place.name,
                           place=place,
                           posts=place_posts,
                           comments=place_comments,
                           comment_form=comment_form,
                           popular_places=popular_places)


@app.route('/add_place', methods=['GET', 'POST'])
@login_required
def add_place():
    form = PlaceForm()
    if form.validate_on_submit():
        place_image_url = None
        if form.place_image.data:
            place_image_url = save_place_image(form.place_image.data)

        place = Place.create(
            form.name.data,
            form.description.data,
            form.address.data,
            form.latitude.data,
            form.longitude.data,
            current_user.id,
            place_image_url
        )
        flash('Вы добавили новое место!', 'success')
        return redirect(url_for('place', place_id=place.id))

    popular_places = get_popular_places(5)
    return render_template('places.html',
                           title="Добавить место",
                           form=form,
                           popular_places=popular_places,
                           show_form=True)


@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()

    all_places = Place.get_all()

    if form.validate_on_submit():
        media_files = None
        if form.media_files.data and any(file.filename for file in form.media_files.data):
            media_files = save_media_files(form.media_files.data, max_files=3)

        post = Post.create(
            form.title.data,
            form.content.data,
            current_user.id,
            int(form.place_id.data),
            media_files
        )
        flash('Вы создали публикацию!', 'success')
        return redirect(url_for('index'))

    popular_places = get_popular_places(5)
    return render_template('create_post.html',
                           title="Создать публикацию",
                           form=form,
                           places=all_places,
                           popular_places=popular_places)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user is None or not user.check_password(form.password.data):
            flash('Неверный адрес эл. почты или пароль', 'danger')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')

        flash('Вы успешно авторизовались!', 'success')
        return redirect(next_page)

    popular_places = get_popular_places(5)
    return render_template('auth.html',
                           title="Авторизация",
                           form=form,
                           auth_type="login",
                           popular_places=popular_places)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        if User.get_by_username(form.username.data):
            flash('Учётная запись с этим именем пользователя уже существует.', 'danger')
            return redirect(url_for('register'))

        if User.get_by_email(form.email.data):
            flash('Учётная запись с этим адресом эл. почты уже существует.', 'danger')
            return redirect(url_for('register'))
        avatar = None
        if form.avatar.data:
            avatar = save_profile_image(form.avatar.data)

        user = User.create(
            form.username.data,
            form.email.data,
            form.password.data,
            form.bio.data if form.bio.data else None,
            avatar
        )

        flash('Вы успешно зарегистрировались!', 'success')
        return redirect(url_for('login'))

    popular_places = get_popular_places(5)
    return render_template('auth.html',
                           title="Регистрация",
                           form=form,
                           auth_type="register",
                           popular_places=popular_places)


@app.route('/logout')
def logout():
    logout_user()
    flash('Вы вышли из своей учётной записи.', 'success')
    return redirect(url_for('index'))


# Edit profile
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        user = current_user
        user.username = form.username.data
        user.set_bio(form.bio.data)

        # Handle profile picture upload
        if form.avatar.data:
            avatar_url = save_profile_image(form.avatar.data)
            if avatar_url:
                user.set_avatar(avatar_url)

        flash('Данные профиля обновлены.', 'success')
        return redirect(url_for('user_profile', username=user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.bio.data = current_user.bio

    popular_places = get_popular_places(5)
    return render_template('edit_profile.html',
                           title="Редактировать профиль",
                           form=form,
                           popular_places=popular_places)

@app.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.get_by_id(post_id)
    if post is None:
        return jsonify({'error': 'Post not found'}), 404

    if post.is_liked_by(current_user.id):
        post.unlike(current_user.id)
        action = 'unliked'
    else:
        post.like(current_user.id)
        action = 'liked'

    return jsonify({
        'action': action,
        'likes_count': post.get_likes_count()
    })


@app.route('/like_place/<int:place_id>', methods=['POST'])
@login_required
def like_place(place_id):
    place = Place.get_by_id(place_id)
    if place is None:
        return jsonify({'error': 'Place not found'}), 404

    if place.is_liked_by(current_user.id):
        place.unlike(current_user.id)
        action = 'unliked'
    else:
        place.like(current_user.id)
        action = 'liked'

    return jsonify({
        'action': action,
        'likes_count': place.get_likes_count()
    })


@app.route('/comment_post/<int:post_id>', methods=['POST'])
@login_required
def comment_post(post_id):
    post = Post.get_by_id(post_id)
    if post is None:
        return jsonify({'error': 'Post not found'}), 404

    form = CommentForm()
    print(form.content, form.validate_on_submit(), form.errors)
    if form.validate_on_submit():
        comment = Comment.create(
            form.content.data,
            current_user.id,
            post_id=post.id
        )

        comment_json = {
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'avatar': current_user.avatar
            }
        }

        return jsonify({
            'success': True,
            'comment': comment_json
        })

    return jsonify({'error': 'Invalid form data'}), 400


@app.route('/comment_place/<int:place_id>', methods=['POST'])
@login_required
def comment_place(place_id):
    place = Place.get_by_id(place_id)
    if place is None:
        return jsonify({'error': 'Place not found'}), 404

    form = CommentForm()
    print(form.content, form.validate_on_submit(), form.errors)
    if form.validate_on_submit():
        comment = Comment.create(
            form.content.data,
            current_user.id,
            place_id=place.id
        )

        comment_json = {
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'avatar': current_user.avatar
            }
        }

        return jsonify({
            'success': True,
            'comment': comment_json
        })

    return jsonify({'error': 'Invalid form data'}), 400

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = Place.search(query)

    places_json = []
    for place in results:
        places_json.append({
            'id': place.id,
            'name': place.name,
            'address': place.address,
            'description': place.description[:100] + '...' if len(place.description) > 100 else place.description,
            'image_url': place.image_url
        })

    return jsonify(places_json)

@app.route('/notifications')
@login_required
def get_notifications():
    notifications_data = current_user.get_notifications()

    notifications_json = []
    for notification in notifications_data:
        notifications_json.append({
            'id': notification.id,
            'content': notification.content,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_read': notification.is_read,
            'type': notification.notification_type,
            'object_id': notification.object_id
        })

    return jsonify(notifications_json)


@app.route('/mark_notification_read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.get_by_id(notification_id)
    if notification is None or notification.user_id != current_user.id:
        return jsonify({'error': 'Notification not found'}), 404

    notification.mark_as_read()
    return jsonify({'success': True})


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
