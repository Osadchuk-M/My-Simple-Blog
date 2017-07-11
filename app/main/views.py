from flask import render_template, request, current_app, flash

from . import main
from ..models import Post, Comment, Widget


@main.route('/')
def home():
    search = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)
    widget = Widget.query.first()
    if search:
        posts = Post.query.whoosh_search(search).all()
        if posts:
            return render_template('index.html', posts=posts, widget=widget, search=search)
        else:
            flash('No results for your query.')
            return render_template('index.html', widget=widget, search=search)
    else:
        pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
        )
        posts = pagination.items
        return render_template('index.html', posts=posts, pagination=pagination, widget=widget)


@main.route('/post/<slug>')
def post(slug):
    post = Post.query.filter_by(slug=slug).first()
    comments = Comment.query.order_by(Comment.timestamp.desc()).filter_by(post_id=post.id).all()
    widget = Widget.query.first()
    return render_template('post.html', post=post, comments=comments, widget=widget)
