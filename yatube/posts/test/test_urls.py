from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post
from .utils import (check_urls_access, check_urls_templates,
                    chek_unexisting_page)

User = get_user_model()


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='test_auth')
        cls.user2 = User.objects.create_user(username='test_not_auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый.текст.поста',
            author=cls.user1,
            group=cls.group,
        )
        cls.guest_client = Client()
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.user1)
        cls.authorized_client_not_author = Client()
        cls.authorized_client_not_author.force_login(cls.user2)

        cls.template_url_names_for_guest = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user1.username}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
        }

        cls.templates_url_names_for_autorized = {
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

    def test_urls_correct_for_guest_client(self):
        """Доступность всех адресов для неавторизованого пользователя"""
        static_urls = [
            '/about/author/',
            '/about/tech/',
        ]
        urls = list(self.template_url_names_for_guest.keys()) + static_urls

        check_urls_access(
            self,
            StaticURLTests.guest_client,
            urls
        )

    def test_urls_correct_for_autorized_client(self):
        """Доступность адресов для авторизованого пользователя (автора)."""

        urls = (list(self.template_url_names_for_guest)
                + list(self.templates_url_names_for_autorized))

        check_urls_access(
            self,
            StaticURLTests.authorized_client_author,
            urls
        )

    def test_urls_not_access_for_guest(self):
        """Недоступность страниц для неавторизованного пользователя."""

        for adress in self.templates_url_names_for_autorized.keys():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_not_access_for_not_author(self):
        """Недоступность страниц для авториз. пользователя (не атвора)."""

        response = self.authorized_client_not_author.get(
            f'/posts/{StaticURLTests.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_templates_for_guest_client(self):
        """Доступность адресов по шаблонам для неавториз. пользователя."""

        names = self.template_url_names_for_guest

        check_urls_templates(
            self,
            StaticURLTests.guest_client,
            names
        )

    def test_urls_templates_for_autorized_client(self):
        """Доступность адресов по шаблонам для авториз. пользователя."""

        names = {
            **self.template_url_names_for_guest,
            **self.templates_url_names_for_autorized
        }

        check_urls_templates(
            self,
            StaticURLTests.authorized_client_author,
            names
        )

    def test_unexising_page(self):
        """Несуществующие страницы недоступны."""
        chek_unexisting_page(self, StaticURLTests.guest_client)
