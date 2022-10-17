import shutil
import tempfile

from django.test import override_settings
from django.contrib.auth.views import redirect_to_login
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from .base_testcase import PostBaseTestCase
from ..models import Post, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(PostBaseTestCase):
    def test_post_create_in_database(self):
        """Cоздаётся новая запись в базе данных."""
        count_posts = Post.objects.count()
        # Заполняем форму
        form_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="form.gif", content=form_gif, content_type="image/gif"
        )
        self.form_data = {
            "text": "Тестовый пост из формы.",
            "group": self.group.id,
            "image": uploaded,
        }
        # Создаём пост
        self.response = self.authorized_client.post(
            self.APP_NAME["create"], data=self.form_data, follow=True
        )
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertRedirects(
            self.response,
            self.APP_NAME["profile"],
        )
        post = Post.objects.first()
        self.assertEqual(post.text, self.form_data["text"])
        self.assertEqual(post.group.id, self.form_data["group"])
        self.assertEqual(post.image.name, self.FORM_IMAGE_URL)
        self.assertEqual(post.author, self.post.author)

    def test_post_edit_in_database(self):
        """Пост редактируется и сохраняется в базе"""
        count_posts = Post.objects.count()
        form_data = {
            "text": "Отредактированный пост.",
            "group": self.group.id,
        }
        response = self.authorized_client.post(
            self.APP_NAME["edit"],
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            self.APP_NAME["post"],
        )
        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), count_posts)
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.group.id, form_data["group"])
        self.assertEqual(post.author, self.post.author)

    def test_post_create_not_auth_redirect(self):
        """При отправке формы неавтор-й user будет перенаправлен"""
        form_data = {
            "text": "Пост из формы, для проверки редиректа",
            "group": self.group.id,
        }
        url = self.APP_NAME["edit"]
        expected_redirect_url = redirect_to_login(url).url
        response = self.client.post(url, form_data)
        self.assertRedirects(response, expected_redirect_url)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)


class PostCommentTests(PostBaseTestCase):
    def test_comment_create_in_database(self):
        """Комментарий появляется в базе данных"""
        count_comments = Comment.objects.count()
        form_data = {"text": "Тестовый комментарий"}
        self.authorized_client.post(
            self.APP_NAME["comment"],
            form_data,
            follow=True,
        )
        comment = Comment.objects.first()
        self.assertEqual(Comment.objects.count(), count_comments + 1)
        self.assertEqual(comment.text, form_data["text"])

    def test_comment_not_create_if_not_auth_user(self):
        """Комментировать посты может только авторизованный пользователь"""
        count_comments = Comment.objects.count()
        form_data = {"text": "Тестовый комментарий"}
        self.client.post(
            self.APP_NAME["comment"],
            form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), count_comments)
