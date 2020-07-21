from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Tag, Character, Series
from series import serializers


# Refractoring the code
class BaseSeriesAttrViewset(viewsets.GenericViewSet,
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
        # return self.queryset.filter(user=self.request.user).order_by('-name')

        # The modifications needed to pass the assigned filter tests
        assigned_only = bool(
            # "assigned_only" gonna be '1' or '0', and in the query_params
            # there is no 'type' concept(like str, int)..there need convert
            # to interger then to Boolean, set default=0
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            # return only tags and characters assigned.
            queryset = queryset.filter(series__isnull=False)

        # To get unique items test pass,
        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

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
class TagViewSet(BaseSeriesAttrViewset):
    """
    Manage tags in the Database
    """
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class CharacterViewSet(BaseSeriesAttrViewset):
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

    # If any function intended as private, provide the fun. name '_fun-name'
    # priv. fun to convert the filter string to intergers.
    def _params_to_ints(self, qs):
        """Convert the List of strings ID's to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrive the series for the authenticated user"""
        # Adding filter feature to API,need extracting the comma seperated
        # strings-convert it to their id(integer), use DB query to filter out.
        # 'query_params'- is variable in request parameter ie a dictionary
        tags = self.request.query_params.get("tags")  # string retrieved
        characters = self.request.query_params.get("characters")

        # refernce the queryset, apply the filtes and return the same
        queryset = self.queryset
        # if tags is not None(default ret. of get())
        if tags:
            tag_ids = self._params_to_ints(tags)
            # Django syntax: filtering on foreignkey objects, tags field has
            # a foreignkey relationship with tags table id, need to filter by
            # that id('__' represents that remote table), 'in'- function
            # to return all the tags that matches with id in given list.
            queryset = queryset.filter(tags__id__in=tag_ids)
        if characters:
            character_ids = self._params_to_ints(characters)
            queryset = queryset.filter(characters__id__in=character_ids)

        return queryset.filter(user=self.request.user)

    # In DRF "get_serializer_class" is the function called to retrieve the
    # serializer class for a particuler request.,if one need to change to diff.
    # serializer class for different actions that are available(detail api)
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        # "self.action"-for 'list', need to use the default 'serializer_class'
        # for action 'retrieve', we need 'SeriesDetailSerializer'
        if self.action == 'retrieve':
            return serializers.SeriesDetailSerializer
        # For image uploading
        elif self.action == 'upload_image':
            return serializers.SeriesImageSerializer
        return self.serializer_class

    # To add create series feature to the series viewset, just add the
    # "perform_create" function.
    def perform_create(self, serializer):
        """Create a new series"""
        serializer.save(user=self.request.user)
        # ModelViewSet allows to create objects-as default., just assaign the
        # authenticated user to it

    # Add a new action: for the image upload Feature, can ovveride or add
    # custom actions, using action decorator.
    # 'detail=True'- only upload images for existing series, in detail url
    # 'series\id\upload-image'
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an Image to a series"""
        # retrive the series object based on id
        series = self.get_object()
        serializer = self.get_serializer(
            series,
            data=request.data
        )

        # valid. provided data correct and no extra-fields
        if serializer.is_valid():
            serializer.save()
            # return content - data, url of the image
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        # if the data is invalid
        # return serializer erors- automatically(auto-valid.) generated by DRF
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
        # update the get_serializer_class also
