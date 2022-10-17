from django.conf import settings

from .base_testcase import PostBaseTestCase


class PostModelTest(PostBaseTestCase):
    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        field_str = {
            self.post.text[: settings.TEXT_SLICE]: str(self.post),
            self.group.title: str(self.group),
        }
        for expected_object_name, expected in field_str.items():
            self.assertEqual(expected_object_name, expected)

    def test_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            "text": "Текст поста",
            "pub_date": "Дата создания",
            "author": "Автор",
            "group": "Группа",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_textes(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            "text": "Введите текст поста",
            "group": "Группа, к которой будет относиться пост",
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )
