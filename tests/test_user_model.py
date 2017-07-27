import os
from datetime import datetime
import time
import unittest

from app import create_app, db
from app.models import User


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user, self.user2 = User(), User()
        db.session.add_all([self.user, self.user2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        self.user.password = 'password'
        self.assertIsNotNone(self.user.password_hash)

    def test_no_password_getter(self):
        self.user.password = 'password'
        with self.assertRaises(AttributeError):
            self.user.password

    def test_password_verification(self):
        self.user.password = 'password'
        self.assertTrue(self.user.verify_password('password'))
        self.assertFalse(self.user.verify_password('bad password'))

    def test_password_hashes(self):
        self.user.password = 'first password'
        self.user2.password = 'second password'
        self.assertNotEquals(self.user.password_hash, self.user2.password_hash)

    def test_timestamp(self):
        new_user = User()
        db.session.add(new_user)
        db.session.commit()
        self.assertLess((datetime.utcnow() - new_user.last_seen).total_seconds(), 3)

    def test_ping(self):
        self.user.last_seen = datetime.utcnow()
        time.sleep(2)
        last_seen_before = self.user.last_seen
        self.user.ping()
        self.assertGreater(self.user.last_seen, last_seen_before)

    def test_is_admin(self):
        self.user.email = os.environ.get('ADMIN_EMAIL')
        self.assertTrue(self.user.is_admin())

    def test_to_json(self):
        self.user.email = 'john@example.com'
        self.user.password = 'password'
        json_user = self.user.to_json()
        expected_keys = ['url', 'username', 'last_seen', 'posts', 'post_count']
        self.assertEqual(sorted(json_user.keys()), sorted(expected_keys))
        self.assertIn('api/v1.0/users/', json_user['url'])
