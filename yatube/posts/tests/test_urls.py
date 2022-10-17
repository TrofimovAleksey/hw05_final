from http import HTTPStatus
from django.test import override_settings

from .base_testcase import PostBaseTestCase


class PostURLTests(PostBaseTestCase):
    # Проверяем общедоступные страницы
    def test_public_urls_exist_at_desired_location(self):
        """URL-адрес возвращает ожидаемый статус-код"""
        for url in self.URL_PUBLIC.values():
            with self.subTest(url=url):
                response = self.client.get(url)
                if url != self.URL_PUBLIC["404"]:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertEqual(
                        response.status_code, HTTPStatus.NOT_FOUND
                    )

    # Проверяем доступность страниц для авторизованного пользователя
    def test_private_urls_exist_at_desired_location(self):
        """Страницы доступны только авторизованному пользователю."""
        for url in self.URL_PRIVATE.values():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_redirect_auth_user_not_author_on_post_detail(self):
        """Страница /posts/post_id/edit/ перенаправит авторизированого
        пользователя, но не автора на страницу поста /posts/post_id/.
        """
        response = self.authorized_client_but_not_author.get(
            self.URL_PRIVATE["edit"], follow=True
        )
        self.assertRedirects(response, self.URL_PUBLIC["post"])

    # Проверяем редиректы для неавторизованного пользователя
    def test_create_url_redirect_anonymous_on_auth_login(self):
        """Страницы перенаправят анонимного пользователя
        на страницу логина.
        """
        url_redirect_names = {
            self.URL_PRIVATE["create"]: self.URL_REDIR["redir_create"],
            self.URL_PRIVATE["edit"]: self.URL_REDIR["redir_edit"],
        }
        for url, redirect_url in url_redirect_names.items():
            with self.subTest(url=url):
                response = self.client.get(url, follow=True)
                self.assertRedirects(response, redirect_url)

    # Проверка вызываемых шаблонов для каждого адреса
    @override_settings(DEBUG=False)
    def test_urls_use_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        url_template_names = {
            self.URL_PUBLIC["index"]: self.TEMPLATE["index"],
            self.URL_PUBLIC["group"]: self.TEMPLATE["group"],
            self.URL_PUBLIC["post"]: self.TEMPLATE["post"],
            self.URL_PUBLIC["profile"]: self.TEMPLATE["profile"],
            self.URL_PUBLIC["404"]: self.TEMPLATE["404"],
            self.URL_PRIVATE["create"]: self.TEMPLATE["create_and_edit"],
            self.URL_PRIVATE["edit"]: self.TEMPLATE["create_and_edit"],
        }
        for url, template in url_template_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
