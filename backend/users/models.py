from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _



class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=200,
        unique=True
    )
    username = models.CharField(
        'Логин пользователя',
        max_length=50,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=50
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=50,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Юзер'
        verbose_name_plural = 'Юзеры'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower',
        verbose_name=_('Пользователь'))
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following',
        verbose_name=_('Автор'))

    def __str__(self):
        return f"{self.user} подписан на {self.author}"

    class Meta():
        ordering = ['-id']
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        models.UniqueConstraint(
            fields=['user', 'author'], name='unique_recording')
