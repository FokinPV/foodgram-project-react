from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
from recipes.models import Recipe
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

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
    def post_delete_method(self, model, serializer, pk, filter):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        author = get_object_or_404(User, id=pk)
        data = {"recipe": recipe.pk,
                "author": author.pk,
                "user": user.pk}
        serializer = serializer(data=data,
                                context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        if self.request.method == 'POST':
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            model.objects.filter(filter & Q(user=user)).delete()
            return Response({'Message:': 'Объект удален'})
