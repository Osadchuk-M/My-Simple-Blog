#!/usr/bin/env python
import os
import flask_whooshalchemy as wa
from app import create_app, db
from app.models import User, Post, Comment, Widget
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
wa.whoosh_index(app, Post)


def make_shell_context():
    return {
        'app': app,
        'db': db,
        'User': User,
        'Post': Post,
        'Comment': Comment,
        'Widget': Widget
    }
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


# @manager.command
# def test(coverage=False):
#     """Run the unit tests."""
#     import unittest
#     tests = unittest.TestLoader().discover('tests')
#     unittest.TextTestRunner(verbosity=2).run(tests)


# @manager.command
# def profile(length=25, profile_dir=None):
#     """Start the application under the code profiler."""
#     from werkzeug.contrib.profiler import ProfilerMiddleware
#     app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
#                                       profile_dir=profile_dir)
#     app.run()


if __name__ == '__main__':
    manager.run()
