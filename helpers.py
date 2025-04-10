import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from models import Place
import json


def get_popular_places(limit=5):
    """Get the most popular places based on likes count."""
    return Place.get_popular(limit)


def allowed_image_file(filename):
    """Check if the file extension is allowed for images."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_video_file(filename):
    """Check if the file extension is allowed for videos."""
    ALLOWED_EXTENSIONS = {'mp4', 'webm', 'ogg'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_file(filename):
    """Check if the file extension is allowed for any media type."""
    return allowed_image_file(filename) or allowed_video_file(filename)


def save_image(file, subfolder='images'):
    """Save an uploaded image and return its URL."""
    if file and allowed_image_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_folder = os.path.join(current_app.static_folder, 'uploads', subfolder)
        file_path = os.path.join(upload_folder, unique_filename)

        os.makedirs(upload_folder, exist_ok=True)

        file.save(file_path)

        return f"/static/uploads/{subfolder}/{unique_filename}"

    return None


def save_video(file):
    """Save an uploaded video and return its URL."""
    if file and allowed_video_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_folder = os.path.join(current_app.static_folder, 'uploads', 'videos')
        file_path = os.path.join(upload_folder, unique_filename)

        os.makedirs(upload_folder, exist_ok=True)

        file.save(file_path)

        return f"/static/uploads/videos/{unique_filename}"

    return None


def save_media_files(files, max_files=3):
    """Save multiple media files and return their URLs as a JSON string."""
    media_urls = []
    count = 0

    for file in files:
        if count >= max_files:
            break

        if allowed_image_file(file.filename):
            url = save_image(file)
            if url:
                media_urls.append({'type': 'image', 'url': url})
                count += 1
        elif allowed_video_file(file.filename):
            url = save_video(file)
            if url:
                media_urls.append({'type': 'video', 'url': url})
                count += 1

    return json.dumps(media_urls) if media_urls else None


def save_profile_image(file):
    """Save a profile image and return its URL."""
    return save_image(file, subfolder='profiles')


def save_place_image(file):
    """Save a place image and return its URL."""
    return save_image(file, subfolder='places')
