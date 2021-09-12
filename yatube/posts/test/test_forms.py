import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, User

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create(username='test_author')
        cls.group = Group.objects.create(
            title='Новое сообщество',
            slug='group1',
            description='Описание нового сообщества',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост 1',
            author=cls.user,
            group=None,
        )

    def setUp(self) -> None:
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTest.user)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post_form(self):
        """Создана новая запись в базе данных"""

        temp_image = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )

        upload_file = SimpleUploadedFile(
            name='test_image.gif',
            content=temp_image,
            content_type='image/gif'
        )

        data_form = {
            'text': 'Тестовый новый пост 222',
            'group': PostFormTest.group.pk,
            'image': upload_file
        }

        self.authorized_client.post(
            reverse('posts:post_create'),
            data=data_form,
            follow=True
        )

        new_post = Post.objects.all().first()
        self.assertEqual(new_post.text, data_form['text'])
        self.assertEqual(new_post.group, PostFormTest.group)
        self.assertIsNotNone(new_post.image)

    def test_edit_post_form(self):
        """Изменение существующего поста"""

        new_post = Post.objects.create(
            text='Новый пост для редактирования',
            author=PostFormTest.user,
            group=PostFormTest.group
        )

        data_form = {
            'text': 'Пост отредактирован',
            'group': PostFormTest.group.pk,
        }

        self.authorized_client.post(
            reverse('posts:post_edit', args=[new_post.pk]),
            data_form,
            follow=True
        )

        new_post.refresh_from_db()
        self.assertEqual(new_post.text, data_form['text'])
        self.assertEqual(new_post.group, PostFormTest.group)


class AddCommentFormTest(TestCase):
    """Testing add comment form"""

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
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment_by_guest(self):
        data_form = {
            'text': 'Тестовый комментарий',
        }

        count_comments = self.post.comments.all().count()

        self.guest_client.post(
            reverse('posts:add_comment', args=[self.post.pk]),
            data_form,
            follow=True
        )

        count_comments_after_post = self.post.comments.all().count()

        self.assertEqual(
            count_comments,
            count_comments_after_post,
            'Комментарий не должен быть добавлен'
        )

    def test_add_comment_by_autorized_client(self):
        data_form = {
            'text': 'Тестовый комментарий',
        }

        count_comments = self.post.comments.all().count()

        self.authorized_client.post(
            reverse('posts:add_comment', args=[self.post.pk]),
            data_form,
            follow=True
        )
        count_comments_after_post = self.post.comments.all().count()

        self.assertEqual(
            count_comments + 1,
            count_comments_after_post,
            'Комментарий должен быть добавлен'
        )

        last_comment = self.post.comments.all().first()

        self.assertEqual(
            last_comment.text, data_form['text'], 'Неверный текст комментария'
        )
