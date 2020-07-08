from rest_framework import generics
# ObtainAuthToken, slight modification needed
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from users.serializers import UserSerializer, AuthTokenSerializer


# Django_rest framework inbuilt,
class CreateUserView(generics.CreateAPIView):
    """
    Create a new user in the system
    """
    serializer_class = UserSerializer


# Auth/Create token View
class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer

    # Set the renderer, can view the Endpoints in the browser
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
