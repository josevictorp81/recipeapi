from rest_framework import serializers

from core.models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'link', 'user']
