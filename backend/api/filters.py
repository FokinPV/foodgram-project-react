from django_filters import rest_framework as filters

from users.models import User
from recipes.models import Favorite, Ingredient, Recipe, ShoppingList


class IngredFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

        def filter_is_favorited(self, queryset, name, value):
            pk = Favorite.objects.filter(
                recipe=self.request.user).values('recipe_id')
            if value:
                return queryset.filter(pk__in=pk)
            return queryset

        def filter_is_in_shopping_cart(self, queryset, name, value):
            pk = ShoppingList.objects.filter(
                user=self.request.user).values('recipe_id')
            if value:
                return queryset.filter(pk__in=pk)
            return queryset
