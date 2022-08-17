from django.test import TestCase
from django.contrib.auth import get_user_model

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
