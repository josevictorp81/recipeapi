from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Tag
from recipe_app.serializers import TagSerializer

TAG_URL = reverse('tag-list')

def detail_url(tag_id):
    return reverse('tag-detail', args=[tag_id])


def create_user(email='test@email.com', password='testpass123'):
    """ cerate and return a user """
    return get_user_model().objects.create_user(email, password)


class PublicTagApiTest(APITestCase):
    """ test unauthenticated api requests """
    def test_list_tag_unauthorized(self):
        """ test user is reqiured """
        self.client = APIClient()
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTest(APITestCase):
    """ test authenticated api requests """
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_tags(self):
        """ test retrieve a list of tags """
        Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='dessert')

        res = self.client.get(TAG_URL)
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_tags_limited_user(self):
        """ test list tags limited to authenticated user """
        user2 = create_user(email='user2@email.com', password='testpassuser2')

        tag = Tag.objects.create(user=self.user, name='fruit')
        Tag.objects.create(user=user2, name='comfort food')

        res = self.client.get(TAG_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)
    
    def test_update_tag(self):
        tag = Tag.objects.create(name='tag3', user=self.user)

        payload = {'name': 'tag new name'}

        url = detail_url(tag_id=tag.id)
        res = self.client.patch(url, payload)

        tag.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, payload['name'])

        
