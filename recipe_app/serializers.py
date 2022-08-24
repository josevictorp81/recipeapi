from rest_framework import serializers

from core.models import Recipe, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """ utilizar quando o usuário tiver a opção de cadastar tags junto com receitas """
    tags = TagSerializer(many=True, required=False) # listar as tags
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'tags']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        """Cria receita e cria as tags"""
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(user=auth_user, **tag)
            recipe.tags.add(tag_obj)

        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'link']


# class RecipeSerializer(serializers.ModelSerializer):
#     tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
#     class Meta:
#         model = Recipe
#         fields = ['id', 'title', 'time_minutes', 'price', 'tags']
#         read_only_fields = ['id']

# class ReadRecipeSerializer(serializers.ModelSerializer):
#     tags = TagSerializer(many=True)
#     class Meta:
#         model = Recipe
#         fields = ['id', 'title', 'time_minutes', 'price', 'tags']
#         read_only_fields = ['id']


# class RecipeDetailSerializer(ReadRecipeSerializer):
#     class Meta(ReadRecipeSerializer.Meta):
#         fields = ReadRecipeSerializer.Meta.fields + ['description', 'link']
