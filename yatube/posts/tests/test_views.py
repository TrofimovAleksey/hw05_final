import math

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.test import Client

from .base_testcase import PostBaseTestCase
from ..models import Follow, User, Group, Post


class PostViewTests(PostBaseTestCase):
    def _assert_list(self, post_from_test):
        self.assertEqual(post_from_test.author, self.post.author)
        self.assertEqual(post_from_test.text, self.post.text)
        self.assertEqual(post_from_test.group, self.post.group)
        self.assertEqual(post_from_test.image.name, self.IMAGE_URL)
        self.assertEqual(post_from_test.pub_date, self.post.pub_date)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            self.APP_NAME["index"]: self.TEMPLATE["index"],
            self.APP_NAME["group"]: self.TEMPLATE["group"],
            self.APP_NAME["profile"]: self.TEMPLATE["profile"],
            self.APP_NAME["post"]: self.TEMPLATE["post"],
            self.APP_NAME["create"]: self.TEMPLATE["create_and_edit"],
            self.APP_NAME["edit"]: self.TEMPLATE["create_and_edit"],
        }
        # Проверяем, что при обращении к name вызывается соответствующий
        # HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяем, что словарь context страницы posts/1
    # содержит ожидаемые значения
    def test_post_detail_page_show_correct_context(self):
        """Шаблон posts:post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.APP_NAME["post"])
        self.assertIn("post", response.context)
        post = response.context["post"]
        self._assert_list(post)

    # Проверяем, что словарь context страницы /create
    # содержит ожидаемые значения
    def test_post_create_page_show_correct_context(self):
        """Шаблон posts:post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.APP_NAME["create"])
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    # Проверяем, что словарь context страницы posts/1/edit
    # содержит ожидаемые значения
    def test_post_edit_page_show_correct_context(self):
        """Шаблон posts:post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.APP_NAME["edit"])
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    # Проверяем, что словарь context страницы /
    # содержит ожидаемые значения
    def test_index_pages_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.APP_NAME["index"])
        post = response.context["page_obj"][0]
        self._assert_list(post)

    # Проверяем, что словарь context страницы group/test-slug
    # содержит ожидаемые значения
    def test_group_list_pages_show_correct_context(self):
        """Шаблон posts:group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.APP_NAME["group"])
        post = response.context["page_obj"][0]
        self._assert_list(post)
        self.assertIsInstance(response.context["group"], Group)

    # Проверяем, что словарь context страницы profile/auth
    # содержит ожидаемые значения
    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.APP_NAME["profile"])
        post = response.context["page_obj"][0]
        self._assert_list(post)
        self.assertIsInstance(response.context["author"], User)

    def test_cashe_index_page(self):
        """Страница index хешируется"""
        post = Post.objects.create(
            author=self.user,
            text="Проверка хеширования",
        )
        count_posts = Post.objects.count()
        response_1 = self.authorized_client.get(self.APP_NAME["index"])
        cached_response_content = response_1.content
        post.delete()
        response_after_delete = self.authorized_client.get(
            self.APP_NAME["index"]
        )
        self.assertEqual(Post.objects.count(), count_posts - 1)
        self.assertEqual(
            cached_response_content, response_after_delete.content
        )
        cache.clear()
        response_after_clear = self.authorized_client.get(
            self.APP_NAME["index"]
        )
        self.assertNotEqual(
            cached_response_content, response_after_clear.content
        )

    def test_follow(self):
        """Тест подписки"""
        self.authorized_client_but_not_author.get(
            self.APP_NAME["profile_follow"]
        )
        follow_count = Follow.objects.filter(user=self.not_author).count()
        self.assertEqual(follow_count, 1)

    def test_unfollow(self):
        Follow.objects.create(user=self.not_author, author=self.user)
        self.authorized_client_but_not_author.get(
            self.APP_NAME["profile_unfollow"]
        )
        follow_after_unfollow_count = Follow.objects.filter(
            user=self.not_author
        ).count()
        self.assertEqual(follow_after_unfollow_count, 0)

    def test_post_show_

    def test_follow_show_by_follower_and_no_by_not_follower(self):
        """Тест появления новой записи на странице подписчика
        и её отсутствия у тех кто не подписан"""
        not_follower = User.objects.create_user(username="TimKuk")
        authorized_client_but_not_follower = Client()
        authorized_client_but_not_follower.force_login(not_follower)
        self.authorized_client_but_not_author.get(
            self.APP_NAME["profile_follow"]
        )
        follow_count = Follow.objects.filter(user=self.not_author).count()
        not_follower_count = Follow.objects.filter(user=not_follower).count()
        self.assertEqual(
            follow_count,
            1,
        )
        self.assertEqual(not_follower_count, 0)
        Post.objects.create(author=self.user, text="Тестируем подписку")
        response_follow = self.authorized_client_but_not_author.get(
            self.APP_NAME["follow"],
        )
        response_profile = self.client.get(self.APP_NAME["profile"])
        response_not_follower = authorized_client_but_not_follower.get(
            self.APP_NAME["follow"],
        )
        self.assertEqual(
            response_follow.context["page_obj"][0],
            response_profile.context["page_obj"][0],
        )
        self.assertEqual(
            len(response_not_follower.context["page_obj"].object_list),
            0,
        )


# Проверка работы paginator
class PaginatorViewsTest(PostBaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Post.objects.all().delete()
        cls.number_of_posts = 13
        cls.pages = math.ceil(cls.number_of_posts / settings.POSTS_PER_PAGE)
        cls.post = [
            Post(
                author=cls.user,
                text=f"Тестовый пост {i}",
                group=cls.group,
            )
            for i in range(cls.number_of_posts)
        ]
        cls.post_list = Post.objects.bulk_create(cls.post)

    def _expected_records_on_page(
        self,
        page_num: int,
        num_records: int,
        expected_per_page: int,
        expected_orphans: int = 0,
    ):
        _num_records = max(num_records - expected_orphans, 0)
        expected_num_pages = math.ceil(_num_records / expected_per_page) or 1
        if page_num < expected_num_pages:
            return expected_per_page
        return num_records - (expected_num_pages - 1) * expected_per_page

    def test_pages_contains_posts(self):
        """На странице нужное количество постов"""
        for page in range(self.pages):
            page = page + 1
            posts_on_page = (
                self.authorized_client.get(
                    self.APP_NAME["index"] + f"?page={page}"
                ),
                self.authorized_client.get(
                    self.APP_NAME["group"] + f"?page={page}"
                ),
                self.authorized_client.get(
                    self.APP_NAME["profile"] + f"?page={page}"
                ),
            )
            # Проверка: количество постов на каждой странице.
            for response in posts_on_page:
                with self.subTest(response=response):
                    num_of_posts = self._expected_records_on_page(
                        page, self.number_of_posts, settings.POSTS_PER_PAGE
                    )
                    self.assertEqual(
                        len(response.context["page_obj"]), num_of_posts
                    )


class PageContainsPostTest(PostBaseTestCase):
    def test_index_page_post_have(self):
        response = self.authorized_client.get(self.APP_NAME["index"])
        self.assertIn(
            self.post,
            response.context["page_obj"],
            "Поста нет на главной странице",
        )

    def test_group_list_post_have(self):
        response = self.authorized_client.get(self.APP_NAME["group"])
        self.assertIn(
            self.post,
            response.context["page_obj"],
            "Поста нет на странице группы test-slug",
        )

    def test_profile_post_have(self):
        response = self.authorized_client.get(self.APP_NAME["profile"])
        self.assertIn(
            self.post,
            response.context["page_obj"],
            "Поста нет на странице профиля",
        )

    def test_post_not_have_in_another_group(self):
        response = self.authorized_client.get(self.APP_NAME["group_1"])
        self.assertNotIn(
            self.post,
            response.context["page_obj"],
            "Пост добавился на страницу группы test-slug-1, хотя не должен",
        )
