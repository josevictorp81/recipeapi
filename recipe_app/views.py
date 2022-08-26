from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Ingredient, Recipe, Tag
from .serializers import RecipeSerializer, RecipeDetailSerializer, TagSerializer, IngredientSerialize
# from .serializers import RecipeSerializer, RecipeDetailSerializer, ReadRecipeSerializer, TagSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """ retrieve recipes of authenticated user """
        return self.queryset.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """ return serializer class """
        if self.action == 'list':
            return RecipeSerializer
        # if self.action == 'create':
        #     return RecipeSerializer
        # if self.action == 'retrieve':
        #     return RecipeDetailSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(ListModelMixin, UpdateModelMixin, DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = TagSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Tag.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class IngredientViewSet(ListModelMixin, UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = IngredientSerialize
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ return queryset filter for authenticated user """
        return self.queryset.filter(user=self.request.user)
