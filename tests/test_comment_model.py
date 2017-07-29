from datetime import datetime
import unittest

from app import create_app, db
from app.exceptions import ValidationError
from app.models import Comment


class CommentModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.comment = Comment()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_from_json(self):
        self.comment = Comment.from_json({
            'author_email': 'john@example.com',
            'body': 'Comment body!'
        })
        self.assertIsNotNone(self.comment)
        with self.assertRaises(ValidationError):
            self.comment = Comment.from_json({})

    def test_to_json(self):
        self.comment = Comment(author_email='john@example.com', body='lorem ipsum',
                               timestamp=datetime.utcnow(), post_id=1)
        db.session.add(self.comment)
        db.session.commit()
        json_comment = self.comment.to_json()
        self.assertEqual(self.comment.author_email, json_comment['author'])
        self.comment.author_id = 1
        db.session.add(self.comment)
        db.session.commit()
        json_comment = self.comment.to_json()
        self.assertIn('api/v1.0', json_comment['author'])
        expected_keys = ['url', 'post', 'body', 'timestamp', 'author']
        self.assertEqual(sorted(json_comment.keys()), sorted(expected_keys))

    def test_gravatar(self):
        self.comment.author_email = 'author@example.com'
        self.comment.gravatar()
        self.assertIsNotNone(self.comment.avatar_hash)
        self.assertIn('http://www.gravatar.com/avatar', self.comment.avatar_hash)


if __name__ == '__main__':
    unittest.main()
