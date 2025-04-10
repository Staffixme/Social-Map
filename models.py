from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

users = []
posts = []
places = []
comments = []
notifications = []
likes_post = {}  # {post_id: [user_ids]}
likes_place = {}  # {place_id: [user_ids]}
subscriptions = {}  # {user_id: [user_ids]}


class User(UserMixin):
    def __init__(self, id, username, email, password, bio=None, avatar=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.bio = bio or ""
        self.avatar = avatar or "https://ui-avatars.com/api/?name=" + username
        self.created_at = datetime.utcnow()
        self.last_seen = datetime.utcnow()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_posts(self):
        return [post for post in posts if post.user_id == self.id]

    def get_liked_places(self):
        result = []
        for place_id, users_who_liked in likes_place.items():
            if self.id in users_who_liked:
                place = Place.get_by_id(place_id)
                if place:
                    result.append(place)
        return result

    def get_subscriptions(self):
        user_ids = subscriptions.get(self.id, [])
        return [User.get_by_id(user_id) for user_id in user_ids]

    def is_subscribed_to(self, user_id):
        return user_id in subscriptions.get(self.id, [])

    def subscribe(self, user_id):
        if user_id != self.id:
            if self.id not in subscriptions:
                subscriptions[self.id] = []
            if user_id not in subscriptions[self.id]:
                subscriptions[self.id].append(user_id)

    def unsubscribe(self, user_id):
        if self.id in subscriptions and user_id in subscriptions[self.id]:
            subscriptions[self.id].remove(user_id)

    def get_notifications(self):
        return [n for n in notifications if n.user_id == self.id]

    @classmethod
    def get_by_id(cls, id):
        for user in users:
            if user.id == id:
                return user
        return None

    @classmethod
    def get_by_username(cls, username):
        for user in users:
            if user.username == username:
                return user
        return None

    @classmethod
    def get_by_email(cls, email):
        for user in users:
            if user.email == email:
                return user
        return None

    @classmethod
    def create(cls, username, email, password, bio=None, avatar=None):
        user_id = len(users) + 1
        user = cls(user_id, username, email, password, bio, avatar)
        users.append(user)
        return user


class Post:
    def __init__(self, id, title, content, user_id, place_id, media_files=None):
        self.id = id
        self.title = title
        self.content = content
        self.user_id = user_id
        self.place_id = place_id
        self.media_files = media_files
        self.created_at = datetime.utcnow()

    def get_user(self):
        return User.get_by_id(self.user_id)

    def get_place(self):
        return Place.get_by_id(self.place_id)

    def get_comments(self):
        return [comment for comment in comments if comment.post_id == self.id]

    def get_likes_count(self):
        return len(likes_post.get(self.id, []))

    def is_liked_by(self, user_id):
        return user_id in likes_post.get(self.id, [])

    def like(self, user_id):
        if self.id not in likes_post:
            likes_post[self.id] = []
        if user_id not in likes_post[self.id]:
            likes_post[self.id].append(user_id)
            # Create notification
            notification_id = len(notifications) + 1
            notification = Notification(
                notification_id,
                self.user_id,
                f"User {User.get_by_id(user_id).username} liked your post '{self.title}'",
                "like_post",
                user_id,
                self.id
            )
            notifications.append(notification)

    def unlike(self, user_id):
        if self.id in likes_post and user_id in likes_post[self.id]:
            likes_post[self.id].remove(user_id)

    @classmethod
    def get_by_id(cls, id):
        for post in posts:
            if post.id == id:
                return post
        return None

    @classmethod
    def create(cls, title, content, user_id, place_id, media_files=None):
        post_id = len(posts) + 1
        post = cls(post_id, title, content, user_id, place_id, media_files)
        posts.append(post)
        return post

    @classmethod
    def get_all(cls, limit=None, offset=0):
        sorted_posts = sorted(posts, key=lambda x: x.created_at, reverse=True)
        if limit:
            return sorted_posts[offset:offset + limit]
        return sorted_posts[offset:]


class Place:
    def __init__(self, id, name, description, address, latitude, longitude, user_id, image_url=None):
        self.id = id
        self.name = name
        self.description = description
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.user_id = user_id
        self.image_url = image_url
        self.created_at = datetime.utcnow()

    def get_user(self):
        return User.get_by_id(self.user_id)

    def get_posts(self):
        return [post for post in posts if post.place_id == self.id]

    def get_comments(self):
        return [comment for comment in comments if comment.place_id == self.id]

    def get_likes_count(self):
        return len(likes_place.get(self.id, []))

    def is_liked_by(self, user_id):
        return user_id in likes_place.get(self.id, [])

    def like(self, user_id):
        if self.id not in likes_place:
            likes_place[self.id] = []
        if user_id not in likes_place[self.id]:
            likes_place[self.id].append(user_id)
            # Create notification
            notification_id = len(notifications) + 1
            notification = Notification(
                notification_id,
                self.user_id,
                f"User {User.get_by_id(user_id).username} liked your place '{self.name}'",
                "like_place",
                user_id,
                self.id
            )
            notifications.append(notification)

    def unlike(self, user_id):
        if self.id in likes_place and user_id in likes_place[self.id]:
            likes_place[self.id].remove(user_id)

    def get_rating(self):
        return self.get_likes_count()

    @classmethod
    def get_by_id(cls, id):
        for place in places:
            if place.id == id:
                return place
        return None

    @classmethod
    def create(cls, name, description, address, latitude, longitude, user_id, image_url=None):
        place_id = len(places) + 1
        place = cls(place_id, name, description, address, latitude, longitude, user_id, image_url)
        places.append(place)
        return place

    @classmethod
    def get_all(cls, limit=None, offset=0):
        sorted_places = sorted(places, key=lambda x: len(likes_place.get(x.id, [])), reverse=True)
        if limit:
            return sorted_places[offset:offset + limit]
        return sorted_places[offset:]

    @classmethod
    def get_popular(cls, limit=5):
        return cls.get_all(limit=limit)

    @classmethod
    def search(cls, query):
        query = query.lower()
        return [place for place in places if query in place.name.lower() or query in place.address.lower()]


class Comment:
    def __init__(self, id, content, user_id, post_id=None, place_id=None):
        self.id = id
        self.content = content
        self.user_id = user_id
        self.post_id = post_id
        self.place_id = place_id
        self.created_at = datetime.utcnow()

    def get_user(self):
        return User.get_by_id(self.user_id)

    @classmethod
    def get_by_id(cls, id):
        for comment in comments:
            if comment.id == id:
                return comment
        return None

    @classmethod
    def create(cls, content, user_id, post_id=None, place_id=None):
        comment_id = len(comments) + 1
        comment = cls(comment_id, content, user_id, post_id, place_id)
        comments.append(comment)

        # Create notification
        notification_id = len(notifications) + 1
        if post_id:
            post = Post.get_by_id(post_id)
            notification = Notification(
                notification_id,
                post.user_id,
                f"User {User.get_by_id(user_id).username} commented on your post '{post.title}'",
                "comment_post",
                user_id,
                post_id
            )
            notifications.append(notification)
        elif place_id:
            place = Place.get_by_id(place_id)
            notification = Notification(
                notification_id,
                place.user_id,
                f"User {User.get_by_id(user_id).username} commented on your place '{place.name}'",
                "comment_place",
                user_id,
                place_id
            )
            notifications.append(notification)

        return comment


class Notification:
    def __init__(self, id, user_id, content, notification_type, source_user_id, object_id):
        self.id = id
        self.user_id = user_id
        self.content = content
        self.notification_type = notification_type
        self.source_user_id = source_user_id
        self.object_id = object_id
        self.created_at = datetime.utcnow()
        self.is_read = False

    def mark_as_read(self):
        self.is_read = True

    @classmethod
    def get_by_id(cls, id):
        for notification in notifications:
            if notification.id == id:
                return notification
        return None


def create_sample_data():
    if not users:
        admin = User.create("admin", "admin@example.com", "admin123", "Administrator")
        john = User.create("john", "john@example.com", "john123", "Software Developer")
        jane = User.create("jane", "jane@example.com", "jane123", "Travel Enthusiast")

        eiffel = Place.create(
            "Eiffel Tower",
            "Iconic iron lattice tower located on the Champ de Mars in Paris, France.",
            "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France",
            48.8584,
            2.2945,
            admin.id
        )

        colosseum = Place.create(
            "Colosseum",
            "An oval amphitheatre in the centre of Rome, Italy.",
            "Piazza del Colosseo, 1, 00184 Roma RM, Italy",
            41.8902,
            12.4922,
            john.id
        )

        statue_liberty = Place.create(
            "Statue of Liberty",
            "A colossal neoclassical sculpture on Liberty Island in New York Harbor.",
            "Liberty Island, New York, NY 10004, USA",
            40.6892,
            -74.0445,
            jane.id
        )

        # Create posts
        Post.create(
            "My visit to the Eiffel Tower",
            "I visited the Eiffel Tower today and it was amazing! The view from the top is breathtaking.",
            john.id,
            eiffel.id,
            "https://images.unsplash.com/photo-1543349689-9a4d426bee8e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80"
        )

        Post.create(
            "Colosseum at sunset",
            "The Colosseum looks even more beautiful at sunset. I highly recommend visiting it during this time.",
            jane.id,
            colosseum.id,
            "https://images.unsplash.com/photo-1552832230-c0197dd311b5?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80"
        )

        Post.create(
            "Liberty in New York",
            "The Statue of Liberty is a symbol of freedom and democracy. It's a must-visit landmark in New York.",
            john.id,
            statue_liberty.id,
            "https://images.unsplash.com/photo-1492217072584-7ff26c10eb75?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80"
        )

        # Add likes
        posts[0].like(jane.id)
        posts[1].like(john.id)
        posts[2].like(admin.id)

        places[0].like(john.id)
        places[0].like(jane.id)
        places[1].like(admin.id)
        places[1].like(jane.id)
        places[2].like(admin.id)
        places[2].like(john.id)

        # Add comments
        Comment.create("Great post! I love the Eiffel Tower too.", jane.id, post_id=1)
        Comment.create("I want to visit the Colosseum someday.", admin.id, post_id=2)
        Comment.create("The Statue of Liberty is amazing!", jane.id, post_id=3)

        Comment.create("Best place in Paris!", john.id, place_id=1)
        Comment.create("Historical marvel!", jane.id, place_id=2)
        Comment.create("Symbol of freedom!", john.id, place_id=3)

        # Add subscriptions
        john.subscribe(jane.id)
        jane.subscribe(john.id)
        admin.subscribe(john.id)
        admin.subscribe(jane.id)


create_sample_data()
