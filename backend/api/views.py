from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from api.filters import IngredFilter, RecipeFilter
from api.paginations import LimitPagination
from api.permissions import IsAuthorOrReadOnly
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorite, Ingredient, Recipe, ShoppingList, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Follow

from .mixins import CustomViewSet
from .serializers import (FavoriteSerializer, GetRecipeSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          ShoppingListSerializer, TagSerializer,
                          CreateUserSerializer,  FollowSerializer)

User = get_user_model()


class UsersViewSet(UserViewSet):
    """
    Вьюсет для пользователя.
    """
    serializer_class = CreateUserSerializer

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        print('test')
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        user = request.user
        is_subscribe = Follow.objects.filter(
            user=user, author=author).exists()
        if request.method == 'POST':
            if is_subscribe or user == author:
                return Response({
                    'errors': ('Вы уже подписаны на этого пользователя')
                }, status=status.HTTP_400_BAD_REQUEST)
            subscribe = Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(
                subscribe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if is_subscribe:
            Follow.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            'errors': 'Вы не подписаны на этого пользователя'
        }, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(CustomViewSet):
    """
    Вьюсет для тэгов.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(CustomViewSet):
    """
    Вьюсет для ингридиентов.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredFilter
    permission_classes = (AllowAny, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для рецептов, избранного и корзины.
    """
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthorOrReadOnly, )
    filterset_class = RecipeFilter
    pagination_class = LimitPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetRecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                data = {'errors': 'Рецепт уже есть в списке покупок!'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            favorite = Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(favorite,
                                            context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favlist = Favorite.objects.filter(user=user, recipe=recipe)
        if request.method == 'DELETE':
            if not favlist.exists():
                data = {'errors': 'Рецепта нет в избранном'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            favlist.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
                data = {'errors': 'Рецепт уже есть в списке!'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            shoplist = ShoppingList.objects.create(user=user, recipe=recipe)
            serializer = ShoppingListSerializer(shoplist,
                                                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        shoplist = ShoppingList.objects.filter(
            user=user, recipe=recipe
        )
        if request.method == 'DELETE':
            if not shoplist.exists():
                data = {'errors': 'В шоплисте нет этого рецепта!'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            shoplist.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        cart_list = []
        text = 'Список покупок:\n\n'
        user = request.user
        ingredients = Ingredient.objects.filter(
            recipe__list__user=user).values(
            'name',
            measurement=F('measurement_unit')
        ).annotate(total=Sum('ingredinrecipe__amount'))
        for _ in ingredients:
            cart_list.append(
                f'{_["name"]}: {_["total"]} {_["measurement"]}'
            )
        text += '\n'.join(cart_list)
        filname = 'shopping_list.txt'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filname}'

        return response
