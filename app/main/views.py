from flask import render_template, request, current_app

from . import main
from ..models import Post, Comment


@main.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination)


@main.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.order_by(Comment.timestamp.desc()).filter_by(post_id=post_id).all()
    return render_template('post.html', post=post, comments=comments)
