from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status


CREATE_USER_URL = reverse('create-user')
CREATE_TOKEN_URL = reverse('token')
ME_URL = reverse('me')

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
    
    def test_create_token_user(self):
        """ test create token with valid creadentials """
        user = {'email': 'test@email.com', 'password': 'testpassword', 'name': 'testname'}
        payload = {'email': user['email'], 'password': user['password']}

        create_user(**user)

        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)
    
    def test_create_token_error(self):
        """ test create token invalid creadentials """
        user = {'email': 'test@email.com', 'password': 'testpassword', 'name': 'testname'}
        payload = {'email': user['email'], 'password': 'testpassworf'}

        create_user(**user)

        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)
    
    def test_create_token_email_not_found(self):
        """Test error returned if user not found for given email."""
        payload = {'email': 'test@email.com', 'password': 'testpassword'}
        
        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)
    
    def test_create_token_blank_password(self):
        """ test create token no user created """
        payload = {'email': 'test@email.com', 'password': ''}

        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)
    
    def test_retrieve_user_unautorized(self):
        """ test authentication is required for users """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email='test@email.com', password='testpassword', name='testname')
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_profile_success(self):
        """ test retrieving profile for logged user """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'id': self.user.id, 'name': self.user.name, 'email': self.user.email})
    
    def test_post_me_not_allowed(self):
        """ test post method not allowed for the endpoint """
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_update_user_profile(self):
        """ test update the user profile for the authenticated user """
        payload = {'password': 'testpasswordupdate', 'name': 'testnameupdate'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
