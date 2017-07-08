from flask import render_template, request, current_app

from . import main
from ..models import Post, Comment, Widget


@main.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    widget = Widget.query.first()
    return render_template('index.html', posts=posts, pagination=pagination, widget=widget)


@main.route('/post/<slug>')
def post(slug):
    post = Post.query.filter_by(slug=slug).first()
    comments = Comment.query.order_by(Comment.timestamp.desc()).filter_by(post_id=post.id).all()
    widget = Widget.query.first()
    return render_template('post.html', post=post, comments=comments, widget=widget)
