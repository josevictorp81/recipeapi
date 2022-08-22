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


def create_user(**params):
    """ create a user """
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(email='test@email.com', password='testpassword')
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
        user2 = create_user(email='test2@email.com', password='testpassword2')

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
    
    def test_create_recipe(self):
        """ test create recipe """
        payload = {'title': 'test recipe', 'price': Decimal('6.99'), 'time_minutes': 9}

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        
        self.assertEqual(recipe.user, self.user)
    
    def test_partial_update_recipe(self):
        """ test partial update of a recipe """
        orignal_link = 'https://exemple.com/recipe/recipe.pdf'
        recipe = create_recipe(user=self.user, title='test recipe title', link=orignal_link)
        
        payload = {'title': 'test recipe new title'}

        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, orignal_link)
        self.assertEqual(recipe.user, self.user)
    
    def test_full_update_recipe(self):
        recipe = create_recipe(user=self.user, title='test recipe title', link='https://exemple.com/recipe/recipe.pdf', description='test')

        payload = {'title': 'test recipe new title', 'link': 'https://exemple.com/recipe/new-recipe.pdf',  'description': 'test new', 'time_minutes': 7, 'price': Decimal('8.34')}

        url = detail_url(recipe_id=recipe.id)
        res = self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)
    
    def test_update_user_error(self):
        """ test change user error for a recipe """
        new_user = create_user(email='test2@email.com', password='testpass123')

        payload = {'user': new_user.id}

        recipe = create_recipe(user=self.user)
        url = detail_url(recipe_id=recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)
    
    def test_delete_recipe(self):
        """ test delete recipe """
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe_id=recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())
    
    def test_delete_recipe_error_other_user(self):
        """ test delete recipe other user """
        new_user = create_user(email='test2@email.com', password='testpass123')

        recipe = create_recipe(user=new_user)

        url = detail_url(recipe_id=recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

