from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from django.contrib.auth import get_user_model

from .serializers import UserSerializer, TokenSerializer


class CreateUserView(CreateAPIView):
    """ create user in system """
    serializer_class = UserSerializer
    queryset = get_user_model().objects.last()


class CreateTokenView(ObtainAuthToken):
    """ create a token for user """
    serializer_class = TokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
