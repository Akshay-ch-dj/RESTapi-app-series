from rest_framework import generics, authentication, permissions
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
    """
    Create a new auth token for user
    """
    serializer_class = AuthTokenSerializer

    # Set the renderer, can view the Endpoints in the browser
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


# For createing manage user endpoints
class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    Manage the authenticated USER
    """
    serializer_class = UserSerializer

    # For authentication and permission
    # The mechanism by which the authentication happens, there is cookie auth.
    # Here it is token authentication
    # permissions are the level of access the user has
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    # Get object function to the API view:- get the model for the logged in usr
    # override the get(), just to return the user ie authenticated
    def get_object(self):
        """Retrive and return authenticated User"""
        # When the object gets called the request will have the user attached
        # (the logged in user who makes the request) cz of the auth._classes
        # present - clubs them together(OUT of the box feature of Django&DRF)
        return self.request.user
