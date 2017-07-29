import os
import unittest
from base64 import b64encode
from datetime import datetime

from flask import url_for, json

from app import create_app, db
from app.models import User, Comment


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        os.environ['ADMIN_EMAIL'] = 'osadchuk.m.01@gmail.com'
        os.environ['ADMIN_PASSWORD'] = '1111'
        db.session.add(User(email='osadchuk.m.01@gmail.com', name='Maxim', password='1111'))
        db.session.commit()
        response = self.client.get(
            url_for('api.get_access_token'),
            headers=self.get_api_headers('Maxim', '1111'))
        self.token = json.loads(response.data.decode('utf-8'))['token']
        self.assertIsNotNone(self.token)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_no_auth(self):
        response = self.client.get(url_for('api.get_posts'), content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_users(self):
        # test for users/1
        response = self.client.get(url_for('api.get_user', user_id=1) + '?token=%s' % self.token)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual('Maxim', data['username'])
        expected_keys = ['url', 'username', 'last_seen', 'posts', 'post_count']
        self.assertEqual(sorted(data.keys()), sorted(expected_keys))

        # test for users/1/posts

        response = self.client.get(url_for('api.get_user_posts', user_id=1) + '?token=%s' % self.token)
        self.assertEqual(response.status_code, 404)

    def test_comments(self):
        # test for comments/
        response = self.client.get(url_for('api.get_comments') + '?token=%s' % self.token)
        self.assertEqual(response.status_code, 404)
        comment = Comment(author_email='john@example.com', body='lorem ipsum',
                          timestamp=datetime.utcnow(), post_id=1)
        db.session.add(comment)
        db.session.commit()
        response = self.client.get(url_for('api.get_comments') + '?token=%s' % self.token)
        self.assertNotEqual(response.status_code, 404)

        # test for comments/1
        response = self.client.get(url_for('api.get_comment', comment_id=1) + '?token=%s' % self.token)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
