import os
import unittest

from flask import url_for

from app import create_app, db
from app.models import User, Post, Comment


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('main.home'))
        self.assertIn('Last posts', response.get_data(as_text=True))

    def test_login(self):
        # Log in
        response = self.client.post(url_for('auth.login'), data={
            'email': os.environ.get('ADMIN_EMAIL'),
            'password': os.environ.get('ADMIN_PASSWORD')
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Maxim', data)

        # Log out
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('You have been logged out.', data)

if __name__ == '__main__':
    unittest.main()
