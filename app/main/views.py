from flask import render_template, request, current_app, flash, redirect, url_for, jsonify
from flask_login import current_user

from . import main
from .forms import CommentForm
from .. import db
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
    _post = Post.query.filter_by(slug=slug).first()
    if _post:
        comments = Comment.query.order_by(Comment.timestamp.desc()).filter_by(post_id=_post.id).all()
        widget = Widget.query.first()
        form = CommentForm()
        return render_template('post.html', post=_post, comments=comments, widget=widget, form=form)
    return redirect(url_for('main.home'))


@main.route('/add_comment/<post_slug>', methods=['POST'])
def add_comment(post_slug):
    _post = Post.query.filter_by(slug=post_slug).first()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data,
            author_email=form.email.data,
            post_id=_post.id
        )
        comment.gravatar()
        db.session.add(comment)
        db.session.commit()
        return jsonify({
            'message': {
                'type': 'success',
                'body': 'Your comment has been saved.'
            },
            'comment': {
                'author_email': comment.author_email,
                'avatar_hash': comment.avatar_hash,
                'timestamp': comment.timestamp,
                'body': comment.body
            }
        })
    return jsonify({
        'message': {
            'type': 'fail',
            'body': 'Your comment has not been saved.(Form is not valid)'
        }
    })
