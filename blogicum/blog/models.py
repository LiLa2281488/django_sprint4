from django.db import models

from django.utils import timezone

from django.contrib.auth import get_user_model

User = get_user_model()


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )


class PublishedModelMixin(models.Model):
    """Абстрактная модель. Добвляет флаг is_published."""

    is_published = models.BooleanField(
        default=True,
        help_text=(
            'Снимите галочку, чтобы скрыть публикацию.'
        ),
        verbose_name='Опубликовано')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True
        ordering = ['-pub_date']


class Category(PublishedModelMixin):
    title = models.CharField(verbose_name="Заголовок", max_length=256)
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(
        unique=True,
        help_text=(
            "Идентификатор страницы для URL; "
            "разрешены символы латиницы, цифры, дефис и подчёркивание."
        ),
        verbose_name="Идентификатор")

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Location(PublishedModelMixin):
    name = models.CharField(
        max_length=256,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModelMixin):
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        help_text=(
            'Если установить дату и время в будущем '
            '— можно делать отложенные публикации.'
        ),
        verbose_name='Дата и время публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        models.SET_NULL,
        null=True,
        blank=False,
        related_name='posts',
        verbose_name='Категория'
    )
    image = models.ImageField(
        upload_to='media/',
        blank=True,
        verbose_name='Изображение'
    )

    comment_count = models.IntegerField(
        default=0,
        verbose_name='Количество комментариев'
    )

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
