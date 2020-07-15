from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Character

from series.serializers import CharacterSerializer


CHARACTERS_URL = reverse('series:character-list')


class PublicCharacterApiTests(TestCase):
    """
    Test the publicily available Characters api
    """

    def SetUp(self):
        self.client = APIClient()

    # TEST 1
    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(CHARACTERS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCharacterApiTests(TestCase):
    """
    Test the private characters API
    """

    def setUp(self):
        """Test characters can be retrived by authorized user"""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@akshay.com',
            'testpass'
        )
        # Force authenticate
        self.client.force_authenticate(self.user)

    # TEST 2
    def test_retrieve_characters(self):
        """Test retriving list of characters"""
        # sample charaters
        Character.objects.create(user=self.user, name='Cassandra Railey')
        Character.objects.create(user=self.user, name='Ramsey')

        res = self.client.get(CHARACTERS_URL)

        characters = Character.objects.all().order_by('-name')
        serializer = CharacterSerializer(characters, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # TEST 3
    def charaters_limited_to_user(self):
        """Test that only authenticated users gets the characters"""
        user2 = get_user_model().objects.create_user(
            'test2@akshay.com',
            'testpass123'
        )
        # with unauthenticated user(no reference later, so not assaigned)
        Character.objects.create(user=user2, name='Jennifer Goines')
        # with authenticated user(used for name match,therefore assaigned)
        character = Character.objects.create(user=self.user, name='Catherena')

        res = self.client.get(CHARACTERS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # only one request-data returned
        self.assertEqual(len(res.data), 1)
        # check the name returned
        self.assertEqual(res.data[0]['name'], character.name)
