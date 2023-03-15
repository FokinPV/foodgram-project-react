from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Модель пользователя
    """
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='Email'
    )
    username = models.CharField(
        unique=True,
        max_length=150,
        verbose_name='Юзернейм пользователя'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.get_full_name()


class Follow(models.Model):
    """
    Модель подписок на пользователей
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_by',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow',
            )
        ]
        ordering = ('author_id',)

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
