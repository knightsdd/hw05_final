import shutil
import tempfile
from time import sleep

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import response
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post
from .utils import chek_paginator, find_post_by_text

User = get_user_model()


class PostViewsTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_author')
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
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.template_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                args=[cls.user.username]): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                args=[cls.post.pk]): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                args=[cls.post.pk]): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

    def test_templates_correct_autorized_client(self):
        """Тестируем шаблоны авторизованным пользователем."""

        for reverse_name, template in self.template_names.items():
            with self.subTest(revers_name=reverse_name):
                response = PostViewsTest.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


# -------------------------------------------------------------------
class YatubePagesTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='test_auth_1')
        cls.user_2 = User.objects.create_user(username='test_auth_2')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='group1',
            description='Тестовое описание группы 1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='group2',
            description='Тестовое описание группы 2',
        )

        cls.posts = []
        for i in range(5):
            cls.posts.append(
                Post.objects.create(
                    text=f'Автоматический текст поста {i}',
                    author=cls.user_1,
                    group=cls.group_1
                )
            )

        cls.posts.append(
            Post.objects.create(
                text='Тестовый текст поста 5',
                author=cls.user_2,
                group=cls.group_2,
            )
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_1)

    def test_index_page_show_correct_context(self):
        """Сраница index содержит корректный контекст."""
        client = YatubePagesTest.authorized_client
        response = client.get(reverse('posts:index'))
        first_obj = response.context['page_obj'][0]
        post_text_0 = first_obj.text
        post_author_0 = first_obj.author
        post_group_0 = first_obj.group
        post_pub_date_0 = first_obj.pub_date
        self.assertEqual(post_text_0, self.posts[5].text)
        self.assertEqual(post_author_0, YatubePagesTest.user_2)
        self.assertEqual(post_group_0, YatubePagesTest.group_2)
        self.assertEqual(post_pub_date_0, YatubePagesTest.posts[5].pub_date)

    def test_group_list_page_show_correct_context(self):
        """Сраница group_list содержит корректный контекст."""
        client = YatubePagesTest.authorized_client
        response = client.get(reverse(
            'posts:group_list',
            args=[YatubePagesTest.group_1.slug])
        )
        object_list = response.context['page_obj']

        for post in object_list:
            with self.subTest(post=post.text):
                self.assertEqual(post.group, YatubePagesTest.group_1)

        self.assertEqual(len(object_list), 5)

    def test_profile_page_show_correct_context(self):
        """Сраница profile содержит корректный контекст."""
        client = YatubePagesTest.authorized_client
        response = client.get(reverse(
            'posts:profile',
            args=[YatubePagesTest.user_1.username])
        )
        object_list = response.context['page_obj']

        for post in object_list:
            with self.subTest(post=post.text):
                self.assertEqual(post.author, YatubePagesTest.user_1)

        self.assertEqual(len(object_list), 5)

    def test_post_detail_page_show_correct_context(self):
        """Сраница post_detail содержит корректный контекст для поста 3."""
        client = YatubePagesTest.authorized_client
        response = client.get(reverse(
            'posts:post_detail',
            args=[YatubePagesTest.posts[2].pk])
        )
        obj = response.context['post']
        self.assertEqual(obj.text, YatubePagesTest.posts[2].text)
        self.assertEqual(obj.group, YatubePagesTest.posts[2].group)
        self.assertEqual(obj.author, YatubePagesTest.posts[2].author)

    def test_post_edit_page_show_correct_context(self):
        """Сраница post_edit содержит корректный контекст"""
        client = YatubePagesTest.authorized_client
        response = client.get(reverse(
            'posts:post_edit',
            args=[YatubePagesTest.posts[0].pk])
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        post_id = response.context.get('form').instance.pk
        self.assertEqual(post_id, YatubePagesTest.posts[0].pk)

    def test_create_page_show_correct_context(self):
        """Сраница create содержит корректный контекст"""
        client = YatubePagesTest.authorized_client
        response = client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_additional_index_create_post(self):
        """Дополнительная проверка при создании поста"""
        client = YatubePagesTest.authorized_client
        new_post = Post.objects.create(
            text='Текст дополнителного поста',
            author=YatubePagesTest.user_1,
            group=YatubePagesTest.group_2
        )
        expected_id = new_post.pk

        pages = [
            reverse('posts:index'),
            reverse('posts:profile', args=[new_post.author.username]),
            reverse('posts:group_list', args=[new_post.group.slug])
        ]

        for page in pages:
            with self.subTest(page=page):
                response = client.get(page)
                post = response.context['page_obj'][0]
                self.assertEqual(post.pk, expected_id)

    def test_cache_index_page(self):
        check_text = 'Тестируем кеширование'
        Post.objects.create(
            text=check_text,
            author=self.user_1,
            group=self.group_1
        )
        response = self.authorized_client.get(reverse('posts:index'))
        page_html = response.content
        self.assertFalse(
            find_post_by_text(check_text, page_html),
            'Кеш не работает'
        )
        sleep(20)
        response = self.authorized_client.get(reverse('posts:index'))
        page_html = response.content
        self.assertTrue(
            find_post_by_text(check_text, page_html),
            'Кеш не работает'
        )


# -------------------------------------------------------------------
class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='test_auth_1')
        cls.user_2 = User.objects.create_user(username='test_auth_2')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='group1',
            description='Тестовое описание группы 1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='group2',
            description='Тестовое описание группы 2',
        )

        cls.posts = []
        for i in range(13):
            cls.posts.append(
                Post.objects.create(
                    text=f'Автоматический текст поста {i}',
                    author=cls.user_1,
                    group=cls.group_1
                )
            )

        cls.posts.append(
            Post.objects.create(
                text='Тестовый текст поста 13',
                author=cls.user_2,
                group=cls.group_2,
            )
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_1)

    def test_paginator_on_index_page1(self):
        """Проверка index страницы № 1."""
        chek_paginator(
            self,
            PaginatorViewsTest.authorized_client,
            settings.RECORDS_PER_PAGE,
            reverse('posts:index')
        )

    def test_paginator_on_index_page2(self):
        """Проверка index страницы № 2."""
        chek_paginator(
            self,
            PaginatorViewsTest.authorized_client,
            4,
            reverse('posts:index'),
            True
        )

    def test_paginator_on_group_list_page1(self):
        """Проверка паджинатора group_list страница № 1."""
        chek_paginator(
            self,
            PaginatorViewsTest.authorized_client,
            settings.RECORDS_PER_PAGE,
            reverse(
                'posts:group_list',
                args=[PaginatorViewsTest.group_1.slug])
        )

    def test_paginator_on_group_list_page2(self):
        """Проверка паджинатора group_list страница № 2."""
        chek_paginator(
            self,
            PaginatorViewsTest.authorized_client,
            3,
            reverse(
                'posts:group_list',
                args=[PaginatorViewsTest.group_1.slug]),
            True
        )

    def test_paginator_on_profile_page1(self):
        """Проверка паджинатора profile страница № 1."""
        chek_paginator(
            self,
            PaginatorViewsTest.authorized_client,
            settings.RECORDS_PER_PAGE,
            reverse(
                'posts:profile',
                args=[PaginatorViewsTest.user_1.username])
        )

    def test_paginator_on_profile_page2(self):
        """Проверка паджинатора profile страница № 2."""
        chek_paginator(
            self,
            PaginatorViewsTest.authorized_client,
            3,
            reverse(
                'posts:profile',
                args=[PaginatorViewsTest.user_1.username]),
            True
        )


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageViewTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group1',
            description='Тестовое описание',
        )

        temp_image = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.upload_file = SimpleUploadedFile(
            name='test_image.gif',
            content=temp_image,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый.текст.поста',
            author=cls.user,
            group=cls.group,
            image=cls.upload_file
        )
        cls.guest_client = Client()
        cls.temp_names = [
            reverse('posts:index'),
            reverse('posts:profile', args=['test_author']),
            reverse('posts:group_list', args=['group1'])
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_image_on_index_page(self):
        for name in self.temp_names:
            with self.subTest(name=name):
                response = self.guest_client.get(name)
                image = response.context['page_obj'][0].image
                self.assertIsNotNone(image)

    def test_image_on_post_detail(self):
        name = reverse('posts:post_detail', args=['1'])
        response = self.guest_client.get(name)
        image = response.context['post'].image
        self.assertIsNotNone(image)


class CommentViewTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_author')
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

    def setUp(self) -> None:
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_detail_have_comment(self):
        data_form = {
            'text': 'Тестовый комментарий',
        }

        self.authorized_client.post(
            reverse('posts:add_comment', args=[self.post.pk]),
            data_form,
            follow=True
        )

        request = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.pk])
        )

        comment_text = request.context['comments'][0].text

        self.assertEqual(comment_text, data_form['text'])


class FollowTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_follower = User.objects.create_user(
            username='user_follower')
        cls.user_not_follower = User.objects.create_user(
            username='user_not_follower')
        cls.author = User.objects.create_user(username='some_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый.текст.поста',
            author=cls.author,
            group=cls.group,
        )

    def setUp(self) -> None:
        super().setUp()
        self.authorized_client_f = Client()
        self.authorized_client_nf = Client()
        self.authorized_client_f.force_login(self.user_follower)
        self.authorized_client_nf.force_login(self.user_not_follower)

    def test_follow_unfollow(self):
        """Тестируем подписку/отписку."""

        self.authorized_client_f.get(
            reverse('posts:profile_follow', args=[self.author.username])
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_follower).filter(author=self.author).exists(),
            'Подписка не работает'
        )
        self.authorized_client_f.get(
            reverse('posts:profile_unfollow', args=[self.author.username])
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user_follower).filter(author=self.author).exists(),
            'Отписка не работает'
        )

    def test_follow_index_for_followers(self):
        """Тестируем ленту подписок для подписчика"""

        Follow.objects.create(
            user=self.user_follower,
            author=self.author
        )

        new_post = Post.objects.create(
            text='Новый пост для подписчика',
            author=self.author,
            group=self.group,
        )

        response = self.authorized_client_f.get(reverse('posts:follow_index'))
        if not response.context['page_obj']:
            chek_post = None
        else:
            chek_post = response.context['page_obj'][0]
        self.assertEqual(
            new_post, chek_post,
            'Лента не работает для подписчика'
        )

    def test_follow_index_for_not_follower(self):
        """Тестируем ленту подписок для неподписчика"""

        response = self.authorized_client_nf.get(reverse('posts:follow_index'))
        if not response.context['page_obj']:
            is_empty = True
        else:
            is_empty = False
        self.assertTrue(is_empty, "Лента не работает для не подписчика")
