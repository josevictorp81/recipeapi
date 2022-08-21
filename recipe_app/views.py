from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from .serializers import RecipeSerializer, RecipeDetailSerializer

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
        return self.serializer_class
