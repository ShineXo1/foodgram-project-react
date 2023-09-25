from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        'Название продукта',
        max_length=200,
    )
    measurement_point = models.CharField(
        'Еденица измерения',
        max_length=50
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_point'),
                name='unique_name_measurement')
        ]
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('id',)

    def __str__(self):
        return f'{self.name}({self.measurement_point})'


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
        related_name='recipes'
    )
    # ingredients = models.ManyToManyField(
    #     Ingredient,
    #     verbose_name='Продукты',
    #     through='IngredientAmount'
    # )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes',
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
        validators=(
            MinValueValidator(1, 'Минимум одна минута'),
            MaxValueValidator(180, 'Максимум 180 минут'))
    )
    text = models.TextField(
        'Описание рецепта',
    )
    created = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created',)

    def __str__(self):
        return f'Блюдо: {self.name}'


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amounts',
    )
    amount = models.PositiveIntegerField(
        'Количество',
        default=1,
        validators=(
            MinValueValidator(1, 'Минимально 1 ингредиент'),
            MaxValueValidator(30, 'Максимум 30 ингрединтов!')
        )
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_amount')]

    def __str__(self):
        return (f'В рецепте {self.recipe.name} {self.amount} '
                f'{self.ingredient.measurement_point} {self.ingredient.name}')


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='В корзине',
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} add to cart {self.recipe}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorite_recipe'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite',)
        ]

    def __str__(self):
        return f'{self.user} follow {self.recipe}'
