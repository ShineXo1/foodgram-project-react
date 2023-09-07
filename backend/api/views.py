from django.db.models import Sum
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .permissions import IsAuthorOrReadOnly
from recipes.models import FavoriteRecipe, Ingredient, \
    Recipe, ShoppingCart, Tag
from users.models import User, Subscribe
from .filters import RecipeFilter
from .serializers import (IngredientSerializer, RecipeEditSerializer,
                          RecipesSerializer, TagSerializer,
                          UserSubscribeSerializer, UserListSerializer,
                          FavoriteSerializer)


class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method not in SAFE_METHODS:
            return RecipeEditSerializer
        return RecipesSerializer

    @staticmethod
    def create_object(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_object(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object = get_object_or_404(model, user=user, recipe=recipe)
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _create_or_destroy(self, http_method, recipe, key,
                           model, serializer):
        if http_method == 'POST':
            return self.create_object(request=recipe, pk=key,
                                      serializers=serializer)
        return self.delete_object(request=recipe, pk=key, model=model)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        return self._create_or_destroy(
            request.method, request, pk, FavoriteRecipe, FavoriteSerializer
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        return self._create_or_destroy(
            request.method, request, pk, ShoppingCart, RecipesSerializer
        )

    @action(
        methods=('get',),
        detail=False,
        url_path='download_shopping_cart',
        pagination_class=None
    )
    def cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(
                'Корзина пуста', status=status.HTTP_400_BAD_REQUEST)
        text = 'Список покупок \n\n'
        ingredient_name = 'recipe__recipe__ingredient__name'
        ingredient_measure = 'recipe__recipe__ingredient__measurement_point'
        recipe_amount = 'recipe_recipe_amount'
        amount_sum = 'recipe__recipe_amount__sum'
        cart = user.shopping_cart.select_related('recipe').values(
            ingredient_name, ingredient_measure).annotate(Sum(
                recipe_amount)).order_by(ingredient_name)
        for ingredients in cart:
            text += (
                f'{ingredients[ingredient_name]}'
                f' ({ingredients[ingredient_measure]})'
                f' - {ingredients[amount_sum]}\n'
            )
        response = HttpResponse(text, content_type='text/plain')
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class IngredientViewSet(ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(follow__user=request.user)
        if queryset:
            pages = self.paginate_queryset(queryset)
            serializer = UserSubscribeSerializer(pages, many=True,
                                                 context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response('Вы ни на кого не подписаны.',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        change_subscription = Subscribe.objects.filter(
            user=user.id, author=author.id
        )
        if request.method == 'POST':
            if user == author:
                return Response('На себя подписываться нельзя!',
                                status=status.HTTP_400_BAD_REQUEST)
            if change_subscription.exists():
                return Response(f'Вы уже подписаны на {author}',
                                status=status.HTTP_400_BAD_REQUEST)
            subscribe = Subscribe.objects.create(
                user=user,
                author=author
            )
            subscribe.save()
            return Response(f'Вы подписались на {author}',
                            status=status.HTTP_201_CREATED)
        if change_subscription.exists():
            change_subscription.delete()
            return Response(f'Вы больше не подписаны на {author}',
                            status=status.HTTP_204_NO_CONTENT)
        return Response(f'Вы не подписаны на {author}',
                        status=status.HTTP_400_BAD_REQUEST)
