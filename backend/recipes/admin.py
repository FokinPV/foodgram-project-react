from django.contrib import admin

from .models import Favorite, Ingredient, IngredInRecipe, Recipe, Tag


class IngredientInline(admin.TabularInline):
    model = IngredInRecipe


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-empty-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-empty-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'text',
                    'cooking_time', 'favorited')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-empty-'

    inlines = [
        IngredientInline,
    ]

    def favorited(self, obj):
        favorited_count = Favorite.objects.filter(recipe=obj).count()
        return favorited_count

    favorited.short_description = 'Is in favorite'