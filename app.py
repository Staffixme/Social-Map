import os
import json
import logging
from datetime import datetime
from flask import Flask, g
from flask_login import LoginManager, current_user
from werkzeug.middleware.proxy_fix import ProxyFix

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


@app.template_filter('from_json')
def from_json(value):
    if not value:
        return []
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return []


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from models import User, Post, Place, Comment, Notification
import routes


@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.get_by_id(int(user_id))


@app.before_request
def before_request():
    g.user = current_user
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
