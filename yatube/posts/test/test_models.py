from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый.текст.поста',
            author=cls.user,
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает метод __str__."""

        group = PostModelTest.group
        post = PostModelTest.post

        # Ожидаемые имена
        group_name_exp = group.title
        post_name_exp = post.text[:15]

        # Полученые имена
        group_name = str(group)
        post_name = str(post)

        self.assertEqual(
            group_name,
            group_name_exp,
            'Неверное отображение имени группы'
        )
        self.assertEqual(
            post_name,
            post_name_exp,
            'Неверное отображение поста'
        )

    def test_group_have_correct_verbose_name(self):
        """Человекочитаемые имена в модели Group"""

        group = PostModelTest.group

        field_verboses = {
            'title': 'Название группы',
            'slug': 'Уникальное имя группы',
            'description': 'Описание группы',
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name,
                    expected)

    def test_post_have_correct_verbose_name(self):
        """Человекочитаемые имена в модели Post"""
        post = PostModelTest.post

        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',

        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_group_have_correct_help_texts(self):
        """Корректный текст подсказки."""
        group = PostModelTest.group

        field_helps = {
            'title': 'Введите название группы (200 символов макимум)',
            'slug': 'Введите уникальное имя группы '
                    '(допускаются латинские буквы и цифры)',
            'description': 'Введите описание группы',
        }

        for value, expected in field_helps.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_post_have_correct_help_texts(self):
        post = PostModelTest.post

        field_helps = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }

        for value, expected in field_helps.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
