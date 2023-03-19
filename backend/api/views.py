from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Favorite, Ingredient, Recipe, ShoppingList, Tag
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.models import Follow

from api.filters import IngredFilter, RecipeFilter
from api.paginations import LimitPagination
from api.permissions import IsAuthorOrReadOnly

from .mixins import CustomMethodViewSet, CustomViewSet
from .serializers import (CreateUserSerializer, FavoriteSerializer,
                          FollowSerializer, GetRecipeSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          ShoppingListSerializer, TagSerializer)

User = get_user_model()


class UsersViewSet(UserViewSet, CustomMethodViewSet):
    """
    Вьюсет для пользователя.
    """
    serializer_class = CreateUserSerializer

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
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
        return self.post_delete_method(Follow, FollowSerializer, request, id)


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


class RecipeViewSet(viewsets.ModelViewSet, CustomMethodViewSet):
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
        return self.post_delete_method(Favorite, FavoriteSerializer,
                                       request, pk)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        return self.post_delete_method(ShoppingList, ShoppingListSerializer,
                                       request, pk)

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
