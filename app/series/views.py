from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag
from series import serializers


# creating a 'Viewset' view based on generic viewset and use the ListModelMixin
class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
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
