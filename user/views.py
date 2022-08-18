from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer


class CreateUserView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.last()
