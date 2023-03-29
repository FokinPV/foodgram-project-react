from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredInRecipe, Recipe,
                            ShoppingList, Tag)
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from users.models import Follow

User = get_user_model()


class CreateUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')
        model = User

    def validate(self, data):

        if User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError(
                'Этот email занят!')

        if User.objects.filter(username=data.get('user_name')).exists():
            raise serializers.ValidationError(
                'Этот username занят!')
        return data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:

        model = IngredInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeShortInfoSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=False)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class GetRecipeSerializer(serializers.ModelSerializer):
    author = CreateUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredInRecipeSerializer(many=True,
                                           source='ingredinrecipe_set')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredients = IngredInRecipe.objects.filter(recipe=obj)
        return IngredInRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=request.user, recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text', 'ingredients',
            'tags', 'cooking_time', 'is_favorited', 'is_in_shopping_cart')


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username', default=serializers.CurrentUserDefault(),
        read_only=True
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    def validate(self, obj):
        user = self.context.get('request').user
        recipe = obj['recipe']
        favorite = Favorite.objects.filter(user=user, recipe=recipe).exists()
        if self.context.get('request').method == 'POST' and favorite:
            raise serializers.ValidationError(
                'Этот рецепт уже есть в избранном'
            )
        if self.context.get('request').method == 'DELETE' and not favorite:
            raise serializers.ValidationError(
                'Этого рецепта нет в избранном'
            )
        return obj

    def to_representation(self, instance):
        context = {"request": self.context.get("request")}
        return RecipeShortInfoSerializer(instance.recipe, context=context).data

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)


class ShoppingListSerializer(FavoriteSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username', default=serializers.CurrentUserDefault(),
        read_only=True
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta(FavoriteSerializer.Meta):
        model = ShoppingList

    def validate(self, obj):
        user = self.context.get('request').user
        recipe = obj['recipe']
        favorite = ShoppingList.objects.filter(
            user=user, recipe=recipe).exists()
        if self.context.get('request').method == 'POST' and favorite:
            raise serializers.ValidationError(
                'Этот рецепт уже есть в корзине'
            )
        if self.context.get('request').method == 'DELETE' and not favorite:
            raise serializers.ValidationError(
                'Этого рецепта нет в корзине'
            )
        return obj

    def to_representation(self, instance):
        context = {"request": self.context.get("request")}
        return RecipeShortInfoSerializer(instance.recipe, context=context).data


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = CreateUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredInRecipeSerializer(
        many=True, source='ingredinrecipe_set')
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    cooking_time = serializers.IntegerField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text', 'ingredients',
            'tags', 'cooking_time', 'is_favorited', 'is_in_shopping_cart',)

    def validate_ingredients(self, data):
        ingredients_id_list = []
        if not data:
            raise serializers.ValidationError(
                'Добавьте больше одного ингридиента!')
        for ingredient in data:
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    'Количество должно быть больше чем ноль!')
            ingredients_id_list.append(ingredient.get('ingredient')['id'])
        unique_ingredients = set(ingredients_id_list)
        if len(ingredients_id_list) > len(unique_ingredients):
            raise serializers.ValidationError(
                'Ингредиент должен быть уникальный!'
            )
        return data

    def validate_tags(self, data):
        if not data:
            raise serializers.ValidationError(
                'Добавьте хоть один тэг!')
        return data

    def validate_cooking_time(self, data):
        if data <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше ноля!')
        return data

    def add_recipe_ingredient(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredInRecipe.objects.create(
                ingredient_id=ingredient.get('ingredient')['id'],
                recipe=recipe,
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        image = validated_data.pop('image')
        tags_data = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredinrecipe_set')
        recipe = Recipe.objects.create(image=image, **validated_data)
        self.add_recipe_ingredient(ingredients, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags = self.initial_data.get('tags')
        instance.tags.set(tags)
        IngredInRecipe.objects.filter(recipe=instance).all().delete()
        ingredients = validated_data.get('ingredinrecipe_set')
        self.add_recipe_ingredient(ingredients, instance)
        instance.save()
        return instance

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=request.user, recipe=obj).exists()

    def to_representation(self, instance):
        serializer = GetRecipeSerializer(instance)
        return serializer.data


class RecipeInFollowListSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowCheckSubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = ('user', 'author', 'is_subscribed',
                  'recipes', 'recipes_count')

    def validate(self, obj):
        user = obj['user']
        author = obj['author']

        is_subscribed = user.subscribed_to.filter(author_id=author).exists()
        if self.context.get('request').method == 'POST':
            if user == author:
                raise serializers.ValidationError(
                    {'errors': 'Подписка на самого себя не разрешена'}
                )
            if is_subscribed:
                raise serializers.ValidationError(
                    {'errors': 'Вы уже подписаны на этого автора'}
                )
        if self.context.get('request').method == 'DELETE':
            if user == author:
                raise serializers.ValidationError(
                    {'errors': 'Отписка от самого себя не разрешена'}
                )
            if not is_subscribed:
                raise serializers.ValidationError(
                    {'errors': 'Ошибка, вы уже отписались'}
                )
        return obj

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author_id=obj.author).exists()

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.author.id)

        if queryset:
            queryset = Recipe.objects.filter(
                author=obj.author)
        return RecipeShortInfoSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class FollowSerializer(FollowCheckSubscribeSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.user_name')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
