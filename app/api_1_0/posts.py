from flask import jsonify, request, url_for, current_app

from . import api
from .authentication import token_required
from .errors import forbidden
from .. import db
from ..models import Post, Comment


@api.route('/posts/')
@token_required
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    _next = None
    if pagination.has_next:
        _next = url_for('api.get_posts', page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': _next,
        'count': pagination.total
    })


@api.route('/posts/<int:post_id>')
@token_required
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_json())


@api.route('/posts/', methods=['POST'])
@token_required
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, {'Location': url_for('api.get_post', post_id=post.id, _external=True)}


@api.route('/posts/<int:post_id>', methods=['PUT'])
@token_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if g.current_user != post.author:
        return forbidden('Insufficient permissions.')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    return jsonify(post.to_json())


@api.route('/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()


@api.route('/posts/<int:post_id>/comments', methods=['GET'])
@token_required
def get_posts_comments(post_id):
    post = Post.query.get_or_404(post_id)
    comments = post.comments.all()
    return jsonify({'comments': [comment.to_json() for comment in comments]})


@api.route('/posts/<int:post_id>/comments', methods=['POST'])
@token_required
def new_comment(post_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.from_json(request.json)
    comment.gravatar()
    comment.post_id = post.id
    db.session.add(comment)
    db.session.commit()
