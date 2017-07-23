from flask import jsonify
from . import api
from ..models import Comment


@api.route('/comments/')
def get_comments():
    comments = Comment.query.all()
    return jsonify([comment.to_json() for comment in comments])


@api.route('/comments/<int:comment_id>')
def get_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return jsonify(comment.to_json())
