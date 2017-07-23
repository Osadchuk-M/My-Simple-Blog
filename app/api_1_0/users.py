from flask import jsonify
from . import api
from ..models import User


@api.route('/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_json())


@api.route('/users/<int:user_id>/posts')
def get_user_posts(user_id):
    user = User.query.get_or_404(user_id)
    posts = user.posts.all()
    return jsonify([post.to_json() for post in posts])
