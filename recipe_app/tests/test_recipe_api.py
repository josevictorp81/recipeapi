from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal

from core.models import Recipe, Tag, Ingredient
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

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {'title': 'Thai Prawn Curry', 'time_minutes': 30, 'price': Decimal('2.50'), 'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],}
        
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(name=tag['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tag."""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {'title': 'Pongal', 'time_minutes': 60, 'price': Decimal('4.50'), 'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}]}
        
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(name=tag['name'], user=self.user).exists()
            self.assertTrue(exists)
        
    def test_create_tag_on_update(self):
        """ test creating tag when updating a recipe """
        recipe = create_recipe(user=self.user)

        paylod = {'tags': [{'name': 'lunch'}]}

        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, paylod, format='json')
        new_tag = Tag.objects.get(user=self.user, name='lunch')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """ test assigning an existing tag when updateing a recipe """
        tag_breakfeat = Tag.objects.create(user=self.user, name='breakfest')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfeat)

        tag_lunch = Tag.objects.create(user=self.user, name='lunch')

        payload = {'tags':[{'name': 'lunch'}]}
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfeat, recipe.tags.all())
    
    def test_clear_recipe_tags(self):
        """ test clearing a recipe tags """
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)
    
    def test_create_with_new_ingresients(self):
        """ test create a recipe with new ingredients """
        payload = {'title': 'cauliflower', 'time_minutes': 5, 'price': Decimal('8.3'), 'ingredients': [{'name': 'cauliflower'}, {'name': 'salt'}]}

        res = self.client.post(RECIPE_URL, payload, format='json')
        recipes = Recipe.objects.filter(user=self.user)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(user=self.user, name=ingredient['name']).exists()
            self.assertTrue(exists)
        
    def test_create_recipe_with_existing_ingredient(self):
        """ test create a recipe with existing ingredients """
        ingredient = Ingredient.objects.create(user=self.user, name='lemon')

        payload = {'title': 'cauliflower', 'time_minutes': 5, 'price': Decimal('8.3'), 'ingredients': [{'name': 'lemon'}, {'name': 'fish sauce'}]}

        res = self.client.post(RECIPE_URL, payload, format='json')
        recipes = Recipe.objects.filter(user=self.user)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(user=self.user, name=ingredient['name']).exists()
            self.assertTrue(exists)
    
    def test_create_ingredient_on_update_recipe(self):
        """ test create ingredient when update a recipe """
        recipe = create_recipe(user=self.user)

        payload = {'ingredients': [{'name': 'limes'}]}

        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user, name='limes')
        self.assertIn(new_ingredient, recipe.ingredients.all())
    
    def test_update_recipe_assign_ingredients(self):
        """ test assigning an existing ingredient when update a recipe """
        ingredient1 = Ingredient.objects.create(user=self.user, name='pepper')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(user=self.user, name='chili')

        payload = {'ingredients': [{'name': 'chili'}]}

        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """ test clear a recipe ingredients """
        ingredient = Ingredient.objects.create(user=self.user, name='garlic')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {'ingredients': []}

        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(ingredient, recipe.ingredients.all())
        self.assertEqual(recipe.ingredients.count(), 0)
        
