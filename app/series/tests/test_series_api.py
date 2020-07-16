from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Series

from series.serializers import SeriesSerializer


# Variable for series url
SERIES_URL = reverse('series:series-list')


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
