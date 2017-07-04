from flask import render_template

from . import main


@main.route('/')
def home():
    return render_template('index.html')


@main.route('/post/<int:post_id>')
def post(post_id):
    return render_template('post.html')


@main.route('/bootstrap')
def bootstrap_base():
    return render_template('base.html')


@main.route('/base_post')
def base_post():
    return render_template('post.html')
