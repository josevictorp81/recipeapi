from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from core.models import Recipe, Tag, Ingredient

def create_user(email='test@email.com', password='testpassword'):
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):
    def test_create_user_with_email_success(self):
        email = 'test@email.com'
        password = 'testpassword00'

        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.__str__(), email)
    
    def test_create_user_email_normalize(self):
        """ test email in normalize for new user """
        emails = [
            ['test1@EMAIL.com', 'test1@email.com'],
            ['Test2@Email.com', 'Test2@email.com'],
            ['TEST3@EMAIL.COM', 'TEST3@email.com'],
            ['test4@email.COM', 'test4@email.com'],
        ]

        for email, expected in emails:
            user = get_user_model().objects.create_user(email=email, password='testpassword')

            self.assertEqual(user.email, expected)
    
    def test_create_user_no_email(self):
        """ test create a user without email """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None, password='testpassword')

    def test_create_super_user(self):
        """ test create user as superuser """
        user = get_user_model().objects.create_superuser(email='test@email.com', password='testpassword')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """ test create recipe success """
        user = get_user_model().objects.create_user(email='test@email.com', password='testpassword')
        recipe = Recipe.objects.create(user=user, title='test recipe name', time_minutes=5, price=Decimal('6.90'), description='test recipe description')

        self.assertEqual(recipe.__str__(), recipe.title)
    
    def test_create_tag(self):
        """ test create tag """
        user = create_user()
        tag = Tag.objects.create(user=user, name='tag1')

        self.assertEqual(tag.__str__(), tag.name)
    
    def test_create_ingredient(self):
        """ test create ingredient """
        user = create_user()
        ingredient = Ingredient.objects.create(user=user, name='ingredient')

        self.assertEqual(ingredient.__str__(), ingredient.name)
