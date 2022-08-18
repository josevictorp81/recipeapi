from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from .serializers import UserSerializer, TokenSerializer


class CreateUserView(CreateAPIView):
    """ create user in system """
    serializer_class = UserSerializer
    queryset = get_user_model().objects.last()


class CreateTokenView(ObtainAuthToken):
    """ create a token for user """
    serializer_class = TokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(RetrieveUpdateAPIView):
    """ manage user autenticated """
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """ retrieve and return the authenticated user """
        return self.request.user
   