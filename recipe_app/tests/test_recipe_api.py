from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal

from core.models import Recipe
from recipe_app.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe-list')


def create_recipe(user, **params):
    defaults = {'title': 'test recipe', 'time_minutes': 7, 'price': Decimal('7.9'), 'description': 'test', 'link': 'http://test.com/recipe'}
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def detail_url(recipe_id):
    """ return a detail url of recipe """
    return reverse('recipe-detail', args=[recipe_id])


class PublicRecipeAPITest(APITestCase):
    """ test unauthenticated request """
    def test_auth_required(self):
        self.client = APIClient()

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(APITestCase):
    """ test authenticated request """
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email='test@email.com', password='testpassword', name='name test')
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_recipes(self):
        """ test retrieving a list of recipes """
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_list_recipe_limited_to_user(self):
        """ test list of recipes is limited to authenticated user """
        user2 = get_user_model().objects.create_user(email='test2@email.com', password='testpassword2', name='name test2')

        create_recipe(user=user2)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
    
    def test_recipe_detail(self):
        """ get recipe detail """
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe_id=recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
