from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from users.models import Follow

User = get_user_model()


class CustomViewSet(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """
    Кастомный миксин.
    """
    pass


class CustomMethodViewSet:
    """
    Кастомные методы для вьюсетов.
    """
    def post_delete_method(self, model, serializer, request, pk):
        user = request.user
        if model == Follow:
            author = get_object_or_404(User, id=pk)
            is_subscribe = Follow.objects.filter(
                user=user, author=author).exists()
            if request.method == 'POST':
                if is_subscribe or user == author:
                    return Response({
                        'errors': ('Вы уже подписаны на этого пользователя')
                    }, status=status.HTTP_400_BAD_REQUEST)
                subscribe = model.objects.create(user=user, author=author)
                serializer = serializer(
                    subscribe, context={'request': request}
                )
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            if is_subscribe:
                model.objects.filter(user=user, author=author).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({
                'errors': 'Вы не подписаны на этого пользователя'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            recipe = get_object_or_404(Recipe, pk=pk)
            if request.method == 'POST':
                if model.objects.filter(user=user, recipe=recipe).exists():
                    return Response({'errors': 'Рецепт уже есть!'},
                                    status=status.HTTP_400_BAD_REQUEST)
                favorite = model.objects.create(user=user, recipe=recipe)
                serializer = serializer(favorite,
                                        context={'request': request})
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            favlist = model.objects.filter(user=user, recipe=recipe)
            if request.method == 'DELETE':
                if not favlist.exists():
                    return Response({'errors': 'Рецепта нет !'},
                                    status=status.HTTP_400_BAD_REQUEST)
                favlist.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
