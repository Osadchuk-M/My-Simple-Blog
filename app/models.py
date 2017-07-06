import os
from datetime import datetime

from flask_login import UserMixin, AnonymousUserMixin
from markdown import markdown
import bleach
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64))
    name = db.Column(db.String)
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
    is_admin = False

login_manager.anonymous_user = AnonymousUser


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=1)

    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def _bootstrap(reps=100):
        from random import randint, choice
        import forgery_py

        themes = ['abstract', 'animals', 'business', 'cats',
                  'city', 'food', 'nightlife', 'fashion',
                  'people', 'nature', 'sports', 'technics', 'transport']
        posts = [
            Post(
                title=forgery_py.lorem_ipsum.word(),
                body='![image](http://lorempixel.com/900/300/' + choice(themes) + str(randint(1, 10)) + ')' + \
                     forgery_py.lorem_ipsum.sentences(randint(5, 12)),
                timestamp=forgery_py.date.date(True))
            for _ in range(reps)]
        db.session.add_all(posts)
        db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

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
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def _bootstrap(reps=300):
        from random import randint
        import forgery_py
        posts_count = Post.query.count()
        comments = [
            Comment(
                body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                timestamp=forgery_py.date.date(True),
                author_name=forgery_py.name.first_name(),
                post_id=randint(1, posts_count)
            )
            for _ in range(reps)
        ]
        db.session.add_all(comments)
        db.session.commit()

    def __repr__(self):
        return '<Comment from %r, timestamp %r>' % (self.author_name, self.timestamp.strftime('%Y-%m-%d'))
