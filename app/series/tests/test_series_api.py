from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Series, Tag, Character
from series.serializers import SeriesSerializer, SeriesDetailSerializer


# Variable for series url
SERIES_URL = reverse('series:series-list')


# for detail api, need a url with idea
# /api/series/serieses/1, need to pass in this argument(id), at the time of
# creating url, a function for generating series url.
def detail_url(series_id):
    """Returns recipe detail URL"""
    return reverse('series:series-detail', args=[series_id])


# For the Series Detail API view
# only name. no extra "**params" needed
def sample_tag(user, name='Money Heist'):
    """Create and return a sample Tag"""
    return Tag.objects.create(user=user, name=name)


def sample_character(user, name='Berlin'):
    """Create and return a sample character"""
    return Character.objects.create(user=user, name=name)


# Helper function to create a series object with customization
def sample_series(user, **params):
    """Create and return a sample series obj."""
    # 'user' is passed in no need to set default
    defaults = {
        'title': 'Breaking Bad',
        'status': True,
        'watch_rate': 5,
        'rating': 8.00
    }
    # parameter passed - ovverides the existing, '**'coverts to a dict.(kwargs)
    defaults.update(params)

    return Series.objects.create(user=user, **defaults)  # '**' -reverse effect


# Three main tests one to test the authentication is required,to retrive series
# then to make sure objects are passed to authenticated users.
class PublicSeriesApiTests(TestCase):
    """
    Test Unauthenticated Series API access
    """
    def setUp(self):
        self.client = APIClient()

    # TEST 1
    def test_auth_required(self):
        """To test authentication required to access API"""
        # make an unauthenticated request
        res = self.client.get(SERIES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateSeriesApiTests(TestCase):
    """
    Test to retrive the series objects
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@akshay.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    # TEST 2
    def test_retrieve_series(self):
        """Test retrieving a list of Series objects"""
        sample_series(user=self.user)
        sample_series(user=self.user)

        res = self.client.get(SERIES_URL)

        series = Series.objects.all().order_by('-id')
        # 'many=True' need in return a list of data.
        serializer = SeriesSerializer(series, many=True)

        # Assert to find the data matches the serializer
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # TEST 3
    def test_series_limitted_to_user(self):
        """Test retrieving Series objects to user"""
        user2 = get_user_model().objects.create_user(
            'test2@akshay.com',
            'testpass1234'
        )
        sample_series(user=user2)
        sample_series(user=self.user)

        res = self.client.get(SERIES_URL)

        series = Series.objects.filter(user=self.user)
        # pass in the ret. queryset result to serializer, even with only one
        # object, use 'many=True' returned objects always as lists
        serializer = SeriesSerializer(series, many=True)

        # Assert the st.code is 'HTTP_200_OK', only data returned fr auth.usr
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    # TEST 4
    # For the detail series api Viewset
    def test_view_series_detail(self):
        """Test viewing a series detail"""
        series = sample_series(user=self.user)
        # To add an item on many to many fields
        series.tags.add(sample_tag(user=self.user))
        series.characters.add(sample_character(user=self.user))

        url = detail_url(series.id)
        res = self.client.get(url)
        # Assertions
        serializer = SeriesDetailSerializer(series)
        self.assertEqual(res.data, serializer.data)
