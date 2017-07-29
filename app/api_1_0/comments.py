from flask import jsonify
from . import api
from .authentication import token_required
from .errors import not_found
from ..models import Comment


@api.route('/comments/')
@token_required
def get_comments():
    comments = Comment.query.all()
    if comments:
        return jsonify([comment.to_json() for comment in comments])
    return not_found('No comments found.')


@api.route('/comments/<int:comment_id>')
@token_required
def get_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return jsonify(comment.to_json())
