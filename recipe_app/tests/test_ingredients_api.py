from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal

from core.models import Ingredient
from recipe_app.serializers import IngredientSerialize

INGREDIENT_URL = reverse('ingredient-list')

def create_user(email='test@email.com', password='testpass123'):
    """ cerate and return a user """
    return get_user_model().objects.create_user(email, password)


class PublicIngredientsApiTest(APITestCase):
    """ test unauthenticated api requests """
    def test_login_required(self):
        """ test login is required for list ingredients """
        self.client = APIClient()
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(APITestCase):
    """ test unauthenticated api requests """
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_ingredientes(self):
        """ test retrieve a list of ingredients """
        Ingredient.objects.create(user=self.user, name='kale')
        Ingredient.objects.create(user=self.user, name='vanilla')

        res = self.client.get(INGREDIENT_URL)
        ingredients = Ingredient.objects.all()
        serializer = IngredientSerialize(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_ingredients_filter_to_user(self):
        """ test list of ingrefients is limited for user """
        user2 = create_user(email='user2@email.com')
        Ingredient.objects.create(user=user2, name='salt')
        ingredient = Ingredient.objects.create(user=self.user, name='pepper')

        res = self.client.get(INGREDIENT_URL)
        ingredients = Ingredient.objects.filter(user=self.user)
        serializer = IngredientSerialize(ingredients, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)
        self.assertEqual(res.data, serializer.data)
    
    
