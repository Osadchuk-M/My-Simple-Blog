import hashlib
import os
from datetime import datetime
from random import randint, choice
import bleach
import forgery_py
from flask_login import UserMixin, AnonymousUserMixin
from markdown import markdown
from slugify import slugify
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64))
    name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
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

    def _create_slug(self):
        slug = slugify(self.title)
        if not Post.query.filter_by(slug=slug).first():
            self.slug = slug
        else:
            self.slug = slug + '-' + str(self.id)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']
        allowed_attributes = ['alt', 'src']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, attributes=allowed_attributes, strip=True))

    def __repr__(self):
        return '<Post %r, timestamp: %r>' % (self.title, self.timestamp.strftime('%Y-%m-%d'))


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean, default=False)
    author_name = db.Column(db.String(64))
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
                author_name=forgery_py.name.first_name(),
                post_id=randint(1, posts_count)
            )
            for _ in range(reps)
        ]
        [_.gravatar() for _ in comments]
        db.session.add_all(comments)
        db.session.commit()

    def gravatar(self, size=64, default='identicon', rating='g'):
        url = 'http://www.gravatar.com/avatar'
        _hash = self.avatar_hash or hashlib.md5(
            self.author_name.encode('utf-8')).hexdigest()
        self.avatar_hash = '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=_hash, size=size, default=default, rating=rating)

    def __repr__(self):
        return '<Comment from %r, timestamp %r>' % (self.author_name, self.timestamp.strftime('%Y-%m-%d'))


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
