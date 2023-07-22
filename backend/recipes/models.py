from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        'Название продукта',
        max_length=200,
    )
    measurement = models.CharField(
        'Еденица измерения',
        max_length=50
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement'),
                name='unique_name_measurement')
        ]
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('id',)

    def __str__(self):
        return f'{self.name}({self.measurement})'


class Tag(models.Model):
    CIENE = '#e76f51'
    ORANGE = '#f4a261'
    SUNSET = '#e9c46a'
    SEA_GREEN = '#2a9d8f'
    DARK_CYAN = '#264652'
    TEAL = '#003049'
    LEMON_CHIFFON = '#eae2b7'
    YELLOW = '#fcbf49'
    STRONG_ORANGE = '#f77f00'
    PALE_RED = '#d62828'

    COLORS = (
        (CIENE, '#e76f51'),
        (ORANGE, '#f4a261'),
        (SUNSET, '#e9c46a'),
        (SEA_GREEN, '#2a9d8f'),
        (DARK_CYAN, '#264652'),
        (TEAL, '#003049'),
        (LEMON_CHIFFON, '#eae2b7'),
        (YELLOW, '#fcbf49'),
        (STRONG_ORANGE, '#f77f00'),
        (PALE_RED, '#d62828')
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=7,
        choices=COLORS
    )
    slug = models.SlugField(
        'Slug тега',
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipie'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Продукты',
        through='IngredientAmount'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipies',
    )
    image = models.ImageField(
        'Фото блюда',
        upload_to='recipes/images'
    )
    name = models.CharField(
        'Название блюда',
        max_length=200,
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления в минутах',
        default=1,
        validators=(MinValueValidator(1, 'Минимум одна минута'),)
    )
    text = models.TextField(
        'Описание рецепта',
    )
    created = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт',
        verbose_name_plural = 'Рецепты',
        ordering = ('-pub_date',)

    def __str__(self):
        return f'Блюдо: {self.name}'
