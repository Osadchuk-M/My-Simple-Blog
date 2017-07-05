from flask import render_template

from . import main


@main.route('/')
def home():
    return render_template('index.html')


@main.route('/post/<int:post_id>')
def post(post_id):
    return render_template('post.html')
