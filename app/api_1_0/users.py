from flask import jsonify

from . import api
from .authentication import token_required
from .errors import not_found
from ..models import User


@api.route('/users/<int:user_id>')
@token_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_json())


@api.route('/users/<int:user_id>/posts')
@token_required
def get_user_posts(user_id):
    user = User.query.get_or_404(user_id)
    posts = user.posts.all()
    if posts:
        return jsonify([post.to_json() for post in posts])
    return not_found('No posts for that user.')
