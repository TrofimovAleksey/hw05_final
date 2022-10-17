import shutil
import tempfile

from django.urls import reverse
from datetime import date
from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache

from ..models import Post, Group, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostBaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса post/test-slug/
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.group_1 = Group.objects.create(
            title="Тестовая группа 1",
            slug="test-slug-1",
            description="Тестовое описание 1",
        )
        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif", content=cls.small_gif, content_type="image/gif"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
            image=cls.uploaded,
            pub_date=date(2022, 12, 12),
        )
        cls.APP_NAME = {
            "index": reverse("posts:index"),
            "group": reverse(
                "posts:group_list", kwargs={"slug": cls.group.slug}
            ),
            "group_1": reverse(
                "posts:group_list", kwargs={"slug": cls.group_1.slug}
            ),
            "profile": reverse("posts:profile", kwargs={"username": cls.user}),
            "post": reverse(
                "posts:post_detail", kwargs={"post_id": cls.post.id}
            ),
            "create": reverse("posts:post_create"),
            "edit": reverse(
                "posts:post_edit", kwargs={"post_id": cls.post.id}
            ),
            "comment": reverse(
                "posts:add_comment", kwargs={"post_id": cls.post.id}
            ),
            "follow": reverse("posts:follow_index"),
            "profile_follow": reverse(
                "posts:profile_follow", kwargs={"username": cls.user}
            ),
            "profile_unfollow": reverse(
                "posts:profile_unfollow", kwargs={"username": cls.user}
            ),
        }
        cls.TEMPLATE = {
            "index": "posts/index.html",
            "group": "posts/group_list.html",
            "post": "posts/post_detail.html",
            "profile": "posts/profile.html",
            "create_and_edit": "posts/create_post.html",
            "404": "core/404.html",
        }
        cls.URL_PUBLIC = {
            "index": "/",
            "group": "/group/test-slug/",
            "profile": "/profile/auth/",
            "post": f"/posts/{cls.post.id}/",
            "404": "/unexisting_page/",
        }
        cls.URL_PRIVATE = {
            "create": "/create/",
            "edit": f"/posts/{cls.post.id}/edit/",
        }
        cls.URL_REDIR = {
            "redir_create": "/auth/login/?next=/create/",
            "redir_edit": f"/auth/login/?next=/posts/{cls.post.id}/edit/",
        }
        cls.IMAGE_URL = "posts/small.gif"
        cls.FORM_IMAGE_URL = "posts/form.gif"

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        # Создаем пользователя
        self.not_author = User.objects.create_user(username="Alex")
        # Создаем третий клиент
        self.authorized_client_but_not_author = Client()
        # Авторизуем пользователя
        self.authorized_client_but_not_author.force_login(self.not_author)
