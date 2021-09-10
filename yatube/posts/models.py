from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.fields.related import ForeignKey

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text='Введите название группы (200 символов макимум)',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Уникальное имя группы',
        help_text='Введите уникальное имя группы '
                  '(допускаются латинские буквы и цифры)',
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Введите описание группы',
    )

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Загрузите картинку'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )

    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Оставьте комментарий'
    )

    created = models.DateTimeField(
        verbose_name='Дата комментария',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created']


class Follow(models.Model):

    user = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )

    author = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
