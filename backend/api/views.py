from django.contrib.auth import get_user_model
from django.db.models import F, Q, Sum, Exists, OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
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
                          ShoppingListSerializer, TagSerializer,
                          FollowCheckSubscribeSerializer)

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
        author = get_object_or_404(User, id=id)
        return self.post_delete_method(Follow,
                                       FollowCheckSubscribeSerializer,
                                       id, Q(author=author))


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

    def get_queryset(self):
        queryset = (
            Recipe.objects
            .select_related('author')
            .prefetch_related('tags', 'ingredients')
        )
        if self.request.user.is_authenticated:
            return queryset.annotate(
                is_favorited=Exists(Favorite.objects.filter(
                    user=self.request.user, recipe__pk=OuterRef('pk'))
                ),
                is_in_shopping_cart=Exists(ShoppingList.objects.filter(
                    user=self.request.user, recipe__pk=OuterRef('pk'))
                )
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.post_delete_method(Favorite, FavoriteSerializer,
                                       pk, Q(recipe=recipe))

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.post_delete_method(ShoppingList, ShoppingListSerializer,
                                       pk, Q(recipe=recipe))

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
