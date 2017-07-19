from flask import current_app
from flask_login import current_user
from functools import wraps


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.is_admin():
            return func(*args, **kwargs)
        return current_app.login_manager.unauthorized()
    return decorated_view
