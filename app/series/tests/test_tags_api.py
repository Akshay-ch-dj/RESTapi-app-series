from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from series.serializers import TagSerializer

TAGS_URL = reverse('series:tag-list')


# Public API tests
class PublicTagsApiTests(TestCase):
    """
    Test the publicily available tags API
    """

    # Setting up the API client
    def setUp(self):
        self.client = APIClient()

    # TEST 1
    def test_login_required(self):
        """Test that login is required for retriving tags"""
        # unauthenticated req. to Tags API
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    """Test the authorized user Tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@akshay.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    # TEST 2
    def test_retrieve_tags(self):
        """Test retrieving Tags"""
        Tag.objects.create(user=self.user, name='Period')
        Tag.objects.create(user=self.user, name='Adventure')

        res = self.client.get(TAGS_URL)

        # Make query on the model, to compare the results
        tags = Tag.objects.all().order_by('-name')  # Alphabet. order reverse
        # More than one items in the serializer-many=True(to serialize a list)
        serializer = TagSerializer(tags, many=True)

        # Assertions,HTTP stat. code & exp. result
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # TEST 3, To test tags are only limited to authenticated user
    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@akshay.com',
            'testpass123'
        )
        Tag.objects.create(user=user2, name='Comedy')
        tag = Tag.objects.create(user=self.user, name='Sci-fi')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Only one tag is created by auth. user, checking the num. of tags ret.
        self.assertEqual(len(res.data), 1)
        # Make assure the returned tag is created bu the auth. user
        self.assertEqual(res.data[0]['name'], tag.name)
