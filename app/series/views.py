from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Character
from series import serializers


# creating a 'Viewset' view based on generic viewset and use the ListModelMixin
class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """
    Manage tags in the Database
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    # To pass the "test_tags_limited_to_user",need to filter objects-auth. user
    # override get_queryset function
    def get_queryset(self):
        """Return Objects for current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

# To pass the tag tests 4&5, need to add CreateModelMixin[ viewsets are custom.
# by adding mixins], then it needs to override the perform_create,to assign the
# tag to the correct user
    def perform_create(self, serializer):
        """Create a new Tag"""
        # The perform_create fn. can be used to hook into the "create object"
        # process, when a "create object" requested in viewset, this fun. evoke
        # and validated serializer will get passed as an argument, here it sets
        # the saved used to "Authenticated user"
        serializer.save(user=self.request.user)


class CharacterViewSet(viewsets.GenericViewSet,
                       mixins.ListModelMixin,
                       mixins.CreateModelMixin):
    """
    Manage Characters in the Database
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Character.objects.all()
    serializer_class = serializers.CharacterSerializer

    def get_queryset(self):
        """Return object for the current authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    # Just like tags, to pass create character tests(TEST 4&5), need the mixin
    def perform_create(self, serializer):
        """Add a new character"""
        serializer.save(user=self.request.user)
