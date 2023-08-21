import base64

from djoser.serializers import PasswordSerializer, UserCreateSerializer, UserSerializer
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import check_password
from rest_framework import serializers

from recipes.models import Ingredient, IngredientAmount, Recipe, Tag, FavoriteRecipe

from users.models import User, Subscribe


class UserListSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def check_is_subscribed(self, obj):
        return (self.context.get('request').user.is_authenticated
                and Subscribe.objects.filter(
                    user=self.context.get('request').user,
                    author=obj).exists()
                )


class UserCreationSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')
        required_fields = (
            'email', 'id', 'username', 'first_name', 'last_name'
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientPatchCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(required=True)


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id',)
    name = serializers.ReadOnlyField(source='ingredient.name',)
    measurement_point = serializers.ReadOnlyField(
        source='ingredient.measurement_point',
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_point', 'amount')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipesSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientAmountSerializer(many=True)
    author = UserListSerializer(required=True)
    is_in_favorite = serializers.SerializerMethodField('get_is_in_favorite')
    is_in_shopping_cart = serializers.SerializerMethodField('get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_in_favorite(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            favorites = request.user.favorites.filter(recioe=obj)
            return favorites.exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            cart = request.user.favorites.filter(recioe=obj)
            return cart.exists()
        return False


class SubscribeRecipeSerializer(RecipesSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeEditSerializer(RecipesSerializer):
    ingredients = IngredientPatchCreateSerializer(many=True)
    tags = serializers.ListField(write_only=True)


    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def validate(self, data):
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError('Добавьте тег')
        array = []
        for ingredient in ingredients:
            if ingredient.get('amount') <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть больше 0')
            array.append(ingredient.get('id'))
            if len(array) != len(set(array)):
                raise serializers.ValidationError(
                    'Ингредиенты повторяются')
            if len(array) == 0:
                raise serializers.ValidationError(
                    'Должен быть хотя бы один ингредиент')
            return data
        cooking_time = data.get('cooking_time')
        if cooking_time > 300 or cooking_time < 1:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовления блюда от 1 до 300 минут'
            })
        return data

    def add_ingredient(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientAmount.objects.bulk_create([
                IngredientAmount(
                    recipe=recipe,
                    ingredient_id=ingredient.get('id'),
                    amount=ingredient.get('amount'),)
            ])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_ingredient(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.add_ingredient(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)



class FavoriteSerializer(SubscribeRecipeSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return representation(
            self.context,
            instance.recipe,
            SubscribeRecipeSerializer)



class SetPasswordSerializer(PasswordSerializer):
    current_password = serializers.CharField(
        required=True,
        label='Текущий пароль')

    def validate(self, data):
        user = self.context.get('request').user
        if data['new_password'] == data['current_password']:
            raise serializers.ValidationError({
                "new_password": "Пароли не должны совпадать"})
        check_current = check_password(data['current_password'], user.password)
        if check_current is False:
            raise serializers.ValidationError({
                "current_password": "Введен неверный пароль"})
        return data


class UserSubscribeSerializer(UserListSerializer):
    recipes = serializers.SerializerMethodField('recipes_limit')
    recipes_count = serializers.SerializerMethodField('get_recipes_count')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def recipes_limit(self, obj):
        request = self.context.get('request')
        queryset = obj.recipes.all()
        if request:
            recipes_limit = request.query_params.get('recipes_limit', None)
            if recipes_limit:
                queryset = queryset[:int(recipes_limit)]
        serializer = SubscribeRecipeSerializer(queryset, many=True)
        return serializer.data


def representation(context, instance, serializer):
    """Функция для использования в to_representation"""

    request = context.get('request')
    new_context = {'request': request}
    return serializer(instance, context=new_context).data
