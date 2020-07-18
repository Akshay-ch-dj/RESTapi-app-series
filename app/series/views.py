from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Character, Series
from series import serializers


# Refractoring the code
class BaseRecipeAttrViewset(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """
    Base viewset for user owned series attributes
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    # queryset and serializer class are different on both

    # To pass the "test_tags_limited_to_user",need to filter objects-auth. user
    # override get_queryset function
    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    # To pass tag tests 4&5-need to add CreateModelMixin[viewsets are custom.
    # using mixins], then it needs to override the perform_create,to assign the
    # tag to the correct user.
    def perform_create(self, serializer):
        """Create a new object"""
        # The perform_create fn. can be used to hook into the "create object"
        # process, when a "create object" requested in viewset, this fun. evoke
        # and validated serializer will get passed as an argument, here it sets
        # the saved used to "Authenticated user"
        serializer.save(user=self.request.user)


# creating a 'Viewset' view based on generic viewset and use the ListModelMixin
class TagViewSet(BaseRecipeAttrViewset):
    """
    Manage tags in the Database
    """
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class CharacterViewSet(BaseRecipeAttrViewset):
    """
    Manage Characters in the Database
    """
    queryset = Character.objects.all()
    serializer_class = serializers.CharacterSerializer


# All functionality create, retrive, update and view details.so -ModelViewSet-
class SeriesViewSet(viewsets.ModelViewSet):
    """
    Manage Series in Database
    """
    serializer_class = serializers.SeriesSerializer
    queryset = Series.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrive the recipes for the authenticated user"""
        return self.queryset.filter(user=self.request.user)

    # In DRF "get_serializer_class" is the function called to retrieve the
    # serializer class for a particuler request.,if one need to change to diff.
    # serializer class for different actions that are available(detail api)
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        # "self.action"-for 'list', need to use the default 'serializer_class'
        # for action 'retrieve', we need 'SeriesDetailSerializer'
        if self.action == 'retrieve':
            return serializers.SeriesDetailSerializer

        return self.serializer_class
