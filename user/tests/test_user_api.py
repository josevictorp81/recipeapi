from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status


CREATE_USER_URL = reverse('create-user')

def create_user(**params):
    """ create a user """
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_user_sucess(self):
        """ test create user successful """
        payload = {'email': 'test@email.com', 'password': 'testpassword', 'name': 'testname'}

        res = self.client.post(CREATE_USER_URL, payload)
        user = get_user_model().objects.get(email=payload['email'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
    
    def test_user_with_email_exists(self):
        """ test create user alrady exists """
        payload = {'email': 'test@email.com', 'password': 'testpassword', 'name': 'testname'}

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL,  payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_short(self):
        """ test create user with short password """
        payload = {'email': 'test@email.com', 'password': 'tp', 'name': 'testname'}
        
        res = self.client.post(CREATE_USER_URL, payload)
        user = get_user_model().objects.filter(email=payload['email']).exists()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user)

