from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        'Login',
        max_length=50,
        unique=True,
    )
    email = models.CharField(
        'Email',
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=20,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=30
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}, {self.email}'
