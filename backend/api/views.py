import csv

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext as _
from djoser.views import UserViewSet
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from recipes.models import (FavoriteRecipe, Ingredient,
                            Recipe, ShoppingCart, Tag, IngredientAmount)
from users.models import User, Subscribe
from .filters import RecipeFilter, IngredientFilter
from .paginator import FoodgramPafination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeEditSerializer,
                          RecipesSerializer, TagSerializer,
                          UserSubscribeSerializer, SubscribeRecipeSerializer)
from .utils import add_remove


class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (permissions.AllowAny,)
    http_method_names = ('get',)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = FoodgramPafination

    def get_serializer_class(self):
        if self.request.method not in SAFE_METHODS:
            return RecipeEditSerializer
        return RecipesSerializer

    @action(
        methods=['POST', 'DELETE'],
        detail=False,
        url_path=r'(?P<recipe>\d+)/favorite',
        url_name='recipe_favorite',
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, *args, **kwargs):
        self.serializer_class = SubscribeRecipeSerializer
        return add_remove(self, request, 'recipe', FavoriteRecipe, Recipe)

    @action(
        methods=['POST', 'DELETE'],
        detail=False,
        url_path=r'(?P<recipe>\d+)/shopping_cart',
        url_name='recipe_cart',
        permission_classes=[IsAuthenticated]
    )
    def cart(self, request, *args, **kwargs):
        self.serializer_class = SubscribeRecipeSerializer
        return add_remove(self, request, 'recipe', ShoppingCart, Recipe)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated, ],
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_point'
        ).annotate(ingredient_amount=Sum('amount')).values_list(
            'ingredient__name', 'ingredient__measurement_point',
            'ingredient_amount')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="Shoppingcart.csv"')
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        for item in list(ingredients):
            writer.writerow(item)
        return response


class IngredientViewSet(ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None
    http_method_names = ('get',)


class CustomUserViewSet(UserViewSet):

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        queryset = Subscribe.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = UserSubscribeSerializer(page, many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response({'errors':
                            _('Вы не можете подписаться на себя.')},
                            status=status.HTTP_400_BAD_REQUEST)
        if Subscribe.objects.filter(user=user, author=author).exists():
            return Response({'errors':
                            _('Вы уже подписались на автора.')},
                            status=status.HTTP_400_BAD_REQUEST)
        Subscribe.objects.create(user=user, author=author)
        queryset = Subscribe.objects.get(user=request.user, author=author)
        serializer = UserSubscribeSerializer(queryset,
                                             context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def subscribe_del(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if not Subscribe.objects.filter(user=user, author=author).exists():
            return Response({'errors': 'Подписки не существует.'},
                            status=status.HTTP_400_BAD_REQUEST)
        Subscribe.objects.get(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
