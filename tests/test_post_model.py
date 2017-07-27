import unittest

from app import create_app, db
from app.admin.forms import PostForm
from app.exceptions import ValidationError
from app.models import Post


class PostModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.post = Post()
        db.session.add(self.post)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_and_update_slug(self):
        self.post.title = 'My title'
        self.post._create_slug()
        self.assertIsNotNone(self.post.slug)
        old_slug = self.post.slug

        self.post.title = 'My new title'
        self.assertNotEqual(self.post.slug, old_slug)

    def test_create_and_update_from_form(self):
        form = PostForm(title='FormTitle', body='# Body of post')
        self.post.create_from_form(form)
        new_post = Post.query.filter((Post.title == 'FormTitle') | (Post.body == '# Body of post')).first()
        self.assertIsNotNone(new_post)

        form.body.data = '## New post body'
        self.post.update_from_form(form)
        self.assertEqual('## New post body', self.post.body)

    def test_harakiri(self):
        self.post.harakiri()
        self.assertNotIn(self.post, Post.query.all())

    def test_on_changed_body(self):
        self.post.body = '# Post with markdown'
        self.assertEqual('<h1>Post with markdown</h1>', self.post.body_html)

    def test_from_json(self):
        self.assertIsNotNone(Post.from_json({
            'title': 'title from json',
            'body': 'body from json'
        }))
        with self.assertRaises(ValidationError):
            Post.from_json(json_post={})

    def test_to_json(self):
        self.post.title = 'Test title'
        self.post.body = 'Test body'
        self.post.author_id = 1
        post_json = self.post.to_json()
        expected_keys = ['url', 'title', 'timestamp', 'body', 'body_html',
                         'author', 'comments', 'comments_count']

        self.assertEqual(sorted(post_json.keys()), sorted(expected_keys))
        self.assertIn('api/v1.0/users', post_json['author'])
        self.assertIn('api/v1.0/posts/1/comments', post_json['comments'])
        self.assertEqual(self.post.comments.count(), post_json['comments_count'])


if __name__ == '__main__':
    unittest.main()
