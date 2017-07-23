import hashlib
import os
from datetime import datetime
from random import randint, choice
import bleach
import forgery_py
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import Serializer
from markdown import markdown
from slugify import slugify
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager
from .exceptions import ValidationError


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64))
    name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    about_me_md = db.Column(db.Text)
    about_me = db.Column(db.Text)
    photo = db.Column(db.LargeBinary)
    location = db.Column(db.String(64))
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def is_admin(self):
        return self.email == os.environ.get('ADMIN_EMAIL')

    def update_about_me(self, markdown_data):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                            'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                            'h1', 'h2', 'h3', 'p', 'img']
        allowed_attributes = ['alt', 'src']
        self.about_me_md = markdown_data
        self.about_me = bleach.linkify(bleach.clean(
            markdown(markdown_data, output_format='html'),
            tags=allowed_tags, attributes=allowed_attributes, strip=True))

    def update_from_form(self, form):
        self.email = form.email.data
        self.name = form.name.data
        self.location = form.location.data
        self.update_about_me(form.about_me.data)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def to_json(self):
        return {
            'url': url_for('api.get_user', user_id=self.id, _external=True),
            'username': self.name,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', user_id=self.id, _external=True),
            'post_count': self.posts.count()
        }

    def __repr__(self):
        return '<User %r>' % self.name


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):
    def is_admin(self):
        return False


login_manager.anonymous_user = AnonymousUser


class Post(db.Model):
    __tablename__ = 'posts'
    __searchable__ = ['title', 'body']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128))
    slug = db.Column(db.String(256), unique=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=1)

    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def _bootstrap(reps=100):
        themes = ['abstract', 'animals', 'business', 'cats',
                  'city', 'food', 'nightlife', 'fashion',
                  'people', 'nature', 'sports', 'technics', 'transport']
        posts = [
            Post(
                title=forgery_py.lorem_ipsum.word(),
                body='![image](http://lorempixel.com/900/300/' + choice(themes) + '/' + str(randint(1, 10)) + ')' + \
                     forgery_py.lorem_ipsum.sentences(randint(15, 50)),
                timestamp=forgery_py.date.date(True))
            for _ in range(reps)]
        db.session.add_all(posts)
        db.session.commit()
        Post._create_slugs()

    @staticmethod
    def _create_slugs():
        posts = Post.query.all()
        [p._create_slug() for p in posts]
        db.session.add_all(posts)
        db.session.commit()

    @staticmethod
    def update_slug(target, value, old_value, initiator):
        if target.title:
            target._create_slug()

    @staticmethod
    def create_from_form(form, author_id=1):
        post = Post(
            title=form.title.data,
            body=form.body.data,
            author_id=author_id
        )
        db.session.add(post)
        db.session.commit()

    def update_from_form(self, form):
        self.title = form.title.data
        self.body = form.body.data
        db.session.add(self)
        db.session.commit()

    def harakiri(self):
        db.session.delete(self)
        db.session.commit()

    def _create_slug(self):
        try:
            slug = slugify(self.title.decode())
            if not Post.query.filter_by(slug=slug).first():
                self.slug = slug
            else:
                self.slug = slug + '-' + str(self.id)
        except UnicodeEncodeError:
            self.slug = self.id


    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']
        allowed_attributes = ['alt', 'src']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, attributes=allowed_attributes, strip=True))

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        title = json_post.get('title')
        if not body or not title:
            raise ValidationError('Post does not have a title or body')
        return Post(title=title, body=body)

    def to_json(self):
        return {
            'url': url_for('api.get_post', post_id=self.id, _external=True),
            'title': self.title,
            'timestamp': self.timestamp,
            'body': self.body,
            'body_html': self.body_html,
            'author': url_for('api.get_user', user_id=self.author_id, _external=True),
            'comments': url_for('api.get_posts_comments', post_id=self.id, _external=True),
            'comments_count': self.comments.count()
        }

    def __repr__(self):
        return '<Post %r, timestamp: %r>' % (self.title, self.timestamp.strftime('%Y-%m-%d'))


db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Post.title, 'set', Post.update_slug)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean, default=False)
    author_email = db.Column(db.String(64))
    avatar_hash = db.Column(db.String(32))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def _bootstrap(reps=300):
        posts_count = Post.query.count()
        comments = [
            Comment(
                body=forgery_py.lorem_ipsum.sentences(randint(1, 8)),
                timestamp=forgery_py.date.date(True),
                author_email=forgery_py.internet.email_address(),
                post_id=randint(1, posts_count)
            )
            for _ in range(reps)
        ]
        [_.gravatar() for _ in comments]
        db.session.add_all(comments)
        db.session.commit()

    @staticmethod
    def from_json(comment_json):
        body = comment_json.get('body')
        author_email = comment_json.get('author_email')
        if not body or not author_email:
            raise ValidationError('Comment does not have a body or author email')
        return Comment(author_email=author_email, body=body)

    def to_json(self):
        if self.author_id:
            author = url_for('api.get_user', user_id=self.author_id, _external=True)
        else:
            author = self.author_email
        return {
            'url': url_for('api.get_comment', comment_id=self.id, _external=True),
            'post': url_for('api.get_post', post_id=self.post_id, _external=True),
            'body': self.body,
            'timestamp': self.timestamp,
            'author': author,
        }

    def gravatar(self, size=64, default='identicon', rating='g'):
        url = 'http://www.gravatar.com/avatar'
        _hash = self.avatar_hash or hashlib.md5(
            self.author_email.encode('utf-8')).hexdigest()
        self.avatar_hash = '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=_hash, size=size, default=default, rating=rating)

    def __repr__(self):
        return '<Comment from %r, timestamp %r>' % (self.author_email, self.timestamp.strftime('%Y-%m-%d'))


class Widget(db.Model):
    __tablename__ = 'widget'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text())
    last_modified = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def _bootstrap():
        widget = Widget(title=forgery_py.lorem_ipsum.word(), body=forgery_py.lorem_ipsum.sentences(randint(2, 6)))
        db.session.add(widget)
        db.session.commit()

    def __repr__(self):
        return '<Side Widget>'
