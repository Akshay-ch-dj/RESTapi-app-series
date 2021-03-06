from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Series

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

    # TEST 4
    # Test to check validation is performed correctly on create requests
    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'Test tag'}
        # Do an HTTP post
        self.client.post(TAGS_URL, payload)

        # Verify the tag exists
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    # TEST 5
    # Create a tag with an invalid name, eg blank string-> validation error
    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # TEST 6:- assure filter only assaigned tags
    def test_retrieve_tags_assigned_to_series(self):
        """Test Filtering Tags by those assigned to series"""
        # Create two tags one assigned and other unassigned., then test
        tag1 = Tag.objects.create(user=self.user, name="Horror")
        tag2 = Tag.objects.create(user=self.user, name="Musical")

        series = Series.objects.create(
            title="Hill of Haunting House",
            status=False,
            rating=8.50,
            watch_rate=5,
            user=self.user
        )
        series.tags.add(tag1)
        # filter by the tags that are assaigned only.
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    # TEST 7:- Assure no tag is duplicated, only unique tags returned
    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items"""
        tag = Tag.objects.create(user=self.user, name='Cartoon')
        Tag.objects.create(user=self.user, name='Fun')
        series1 = Series.objects.create(
            title="Scooby Doo",
            status=False,
            rating=8.23,
            watch_rate=5,
            user=self.user
        )
        series1.tags.add(tag)
        series2 = Series.objects.create(
            title='Bumble bees',
            status=False,
            rating=8.75,
            watch_rate=5,
            user=self.user
        )
        series2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        # There need a second dummy tag for the transparancy of the test
        self.assertEqual(len(res.data), 1)
