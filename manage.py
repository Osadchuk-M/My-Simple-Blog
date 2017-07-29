#!/usr/bin/env python
import os

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

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


@manager.command
def bootstrap():
    """ Create database with fake data """
    db.create_all()
    Post._bootstrap()
    Comment._bootstrap()
    Widget._bootstrap()
    os.environ['ADMIN_EMAIL'] = 'osadchuk.m.01@gmail.com'
    os.environ['ADMIN_PASSWORD'] = '1111'
    db.session.add(User(email='osadchuk.m.01@gmail.com', name='Maxim', password='1111'))
    db.session.commit()


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


if __name__ == '__main__':
    manager.run()
