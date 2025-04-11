from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Association tables
likes_post = db.Table('likes_post',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                      db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
                      db.Column('created_at', db.DateTime, default=datetime.utcnow)
                      )

likes_place = db.Table('likes_place',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                       db.Column('place_id', db.Integer, db.ForeignKey('place.id'), primary_key=True),
                       db.Column('created_at', db.DateTime, default=datetime.utcnow)
                       )

subscriptions = db.Table('subscriptions',
                         db.Column('subscriber_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                         db.Column('subscribed_to_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                         db.Column('created_at', db.DateTime, default=datetime.utcnow)
                         )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    bio = db.Column(db.Text)
    avatar = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship('Post', backref='user', lazy='dynamic')
    places = db.relationship('Place', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification',
                                    foreign_keys='Notification.user_id',
                                    back_populates='recipient',
                                    lazy='dynamic')

    liked_posts = db.relationship('Post', secondary=likes_post, lazy='dynamic',
                                  backref=db.backref('likes', lazy='dynamic'))
    liked_places = db.relationship('Place', secondary=likes_place, lazy='dynamic',
                                   backref=db.backref('likes', lazy='dynamic'))
    subscribed_to = db.relationship('User', secondary=subscriptions,
                                    primaryjoin=(subscriptions.c.subscriber_id == id),
                                    secondaryjoin=(subscriptions.c.subscribed_to_id == id),
                                    backref=db.backref('subscribers', lazy='dynamic'),
                                    lazy='dynamic')

    def get_posts(self):
        return self.posts.order_by(Post.created_at.desc()).all()

    def get_liked_places(self):
        return self.liked_places.order_by(Place.created_at.desc()).all()

    def subscribe(self, user_id):
        user_to_subscribe = User.query.get(user_id)
        if user_to_subscribe and not self.is_subscribed_to(user_id):
            self.subscribed_to.append(user_to_subscribe)
            db.session.commit()

    def unsubscribe(self, user_id):
        user_to_unsubscribe = User.query.get(user_id)
        if user_to_unsubscribe and self.is_subscribed_to(user_id):
            self.subscribed_to.remove(user_to_unsubscribe)
            db.session.commit()

    def is_subscribed_to(self, user_id):
        return self.subscribed_to.filter(
            subscriptions.c.subscribed_to_id == user_id
        ).count() > 0

    def get_subscriptions(self):
        return self.subscribed_to.order_by(User.username).all()

    def get_notifications(self):
        return self.notifications.order_by(Notification.created_at.desc()).all()

    # Статические методы
    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(int(id))

    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def set_avatar(self, avatar_url):
        if not isinstance(avatar_url, str):
            raise ValueError("Avatar URL must be a string")

        self.avatar = avatar_url
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def set_bio(self, bio_text):
        if not isinstance(bio_text, str):
            raise ValueError("Bio must be a string")

        self.bio = bio_text
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def create(cls, username, email, password, bio=None, avatar=None):
        user = cls(
            username=username,
            email=email,
            bio=bio or "",
            avatar=avatar or f"https://ui-avatars.com/api/?name={username}"
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    # Обновленный метод для проверки пароля
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Метод для обновления времени последнего посещения
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    media_files = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=False)

    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __repr__(self):
        return f'<Post {self.title}>'

    def get_user(self):
        return User.get_by_id(self.user_id)

    def get_place(self):
        return Place.get_by_id(self.place_id)

    def get_comments(self):
        return self.comments.order_by(Comment.created_at.desc()).all()

    def get_likes_count(self):
        return self.likes.count()

    def is_liked_by(self, user_id):
        return db.session.query(likes_post).filter_by(
            post_id=self.id,
            user_id=user_id
        ).count() > 0

    def like(self, user_id):
        if not self.is_liked_by(user_id):
            stmt = likes_post.insert().values(
                post_id=self.id,
                user_id=user_id
            )
            db.session.execute(stmt)

            # Создание уведомления через конструктор
            user = User.get_by_id(user_id)
            notification = Notification(
                user_id=self.user_id,
                source_user_id=user_id,
                content=f"User {user.username} liked your post '{self.title}'",
                notification_type="like_post",
                object_id=self.id
            )
            db.session.add(notification)
            db.session.commit()

    def unlike(self, user_id):
        if self.is_liked_by(user_id):
            # Прямое удаление из ассоциативной таблицы
            stmt = likes_post.delete().where(
                likes_post.c.post_id == self.id,
                likes_post.c.user_id == user_id
            )
            db.session.execute(stmt)
            db.session.commit()

    @classmethod
    def create(cls, title, content, user_id, place_id, media_files=None):
        post = cls(
            title=title,
            content=content,
            user_id=user_id,
            place_id=place_id,
            media_files=media_files
        )
        db.session.add(post)
        db.session.commit()
        return post

    @classmethod
    def get_all(cls, limit=None, offset=0):
        query = cls.query.order_by(cls.created_at.desc())
        if limit is not None:
            query = query.limit(limit).offset(offset)
        return query.all()

    @classmethod
    def get_by_id(cls, id):
        return Post.query.get(int(id))


class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes_count = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    posts = db.relationship('Post', backref='place', lazy='dynamic')
    comments = db.relationship('Comment', backref='place', lazy='dynamic')

    def __repr__(self):
        return f'<Place {self.name}>'

    def get_posts(self):
        return self.posts.order_by(Post.created_at.desc()).all()

    def get_comments(self):
        return self.comments.order_by(Comment.created_at.desc()).all()

    def get_likes_count(self):
        return self.likes.count()

    def is_liked_by(self, user_id):
        return db.session.query(likes_place).filter_by(
            place_id=self.id,
            user_id=user_id
        ).count() > 0

    def like(self, user_id):
        if not self.is_liked_by(user_id):
            stmt = likes_place.insert().values(
                place_id=self.id,
                user_id=user_id
            )
            db.session.execute(stmt)

            # Создание уведомления напрямую
            user = User.get_by_id(user_id)
            db.session.add(Notification(
                user_id=self.user_id,
                source_user_id=user_id,
                content=f"User {user.username} liked your place '{self.name}'",
                notification_type="like_place",
                object_id=self.id
            ))
            db.session.commit()

    def unlike(self, user_id):
        if self.is_liked_by(user_id):
            stmt = likes_place.delete().where(
                likes_place.c.place_id == self.id,
                likes_place.c.user_id == user_id
            )
            db.session.execute(stmt)
            db.session.commit()

    def get_rating(self):
        return self.get_likes_count()

    @classmethod
    def create(cls, name, description, address, latitude, longitude, user_id, image_url=None):
        place = cls(
            name=name,
            description=description,
            address=address,
            latitude=latitude,
            longitude=longitude,
            user_id=user_id,
            image_url=image_url
        )
        db.session.add(place)
        db.session.commit()
        return place

    @classmethod
    def get_all(cls, limit=None, offset=0):
        query = cls.query.order_by(cls.created_at.desc())
        if limit is not None:
            query = query.limit(limit).offset(offset)
        return query.all()

    @classmethod
    def get_popular(cls, limit=5):
        return cls.query.order_by(db.func.coalesce(cls.likes_count, 0).desc()).limit(limit).all()

    @classmethod
    def search(cls, query):
        search_term = f"%{query}%"
        return cls.query.filter(
            (cls.name.ilike(search_term)) |
            (cls.address.ilike(search_term))
        ).all()

    @classmethod
    def get_by_id(cls, id):
        return Place.query.get(int(id))

    def get_user(self):
        return User.get_by_id(self.user_id)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))

    def __repr__(self):
        return f'<Comment {self.content[:20]}>'

    @classmethod
    def create(cls, content, user_id, post_id=None, place_id=None):
        comment = cls(
            content=content,
            user_id=user_id,
            post_id=post_id,
            place_id=place_id
        )
        db.session.add(comment)

        # Создание уведомления
        if post_id:
            post = Post.query.get(post_id)
            notification = Notification(
                user_id=post.user_id,
                source_user_id=user_id,
                content=f"{User.query.get(user_id).username} комментирует вашу публикацию '{post.title}'",
                notification_type="comment_post",
                object_id=post_id
            )
        elif place_id:
            place = Place.query.get(place_id)
            notification = Notification(
                user_id=place.user_id,
                source_user_id=user_id,
                content=f"{User.query.get(user_id).username} комментирует добавленное вами место '{place.name}'",
                notification_type="comment_place",
                object_id=place_id
            )

        db.session.add(notification)
        db.session.commit()
        return comment

    def get_user(self):
        return User.get_by_id(self.user_id)

    @classmethod
    def get_by_id(cls, id):
        return Comment.query.get(int(id))


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    source_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    object_id = db.Column(db.Integer)

    # Явное определение отношений с указанием foreign keys
    recipient = db.relationship('User', foreign_keys=[user_id], back_populates='notifications')
    source_user = db.relationship('User', foreign_keys=[source_user_id])

    def mark_as_read(self):
        self.is_read = True
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def create(cls, user_id, source_user_id, content, notification_type, object_id):
        notification = cls(
            user_id=user_id,
            source_user_id=source_user_id,
            content=content,
            notification_type=notification_type,
            object_id=object_id
        )
        db.session.add(notification)
        db.session.commit()
        return notification


with app.app_context():
    db.create_all()
