from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Ingredient, Recipe, Tag
from .serializers import RecipeSerializer, RecipeDetailSerializer, TagSerializer, IngredientSerialize

class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """ retrieve recipes of authenticated user """
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            queryset = queryset.filter(tags__name__icontains=tags)
        if ingredients:
            queryset = queryset.filter(ingredients__name__icontains=ingredients)
        
        return queryset.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """ return serializer class """
        if self.action == 'list':
            return RecipeSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BaseRecipeAttrViewSet(ListModelMixin, UpdateModelMixin, DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    serializer_class = IngredientSerialize
    queryset = Ingredient.objects.all()

