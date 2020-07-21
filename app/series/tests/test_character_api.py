from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Character, Series

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
    def test_characters_limited_to_user(self):
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

    # TEST 4
    # Tests for adding Character(http post), to test the create character
    # successful, and character invalid
    def test_create_character_successful(self):
        """Test create a new character"""
        payload = {'name': 'Agnes Nielson'}
        self.client.post(CHARACTERS_URL, payload)

        # Check the character gets added or not
        exists = Character.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()
        self.assertTrue(exists)

    # TEST 5
    def test_create_character_invalid(self):
        """Test creating invalid character fails"""
        payload = {'name': ''}
        res = self.client.post(CHARACTERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # TEST 6:- Similer filterig tests as on tags
    def test_retrieve_characters_assigned_to_series(self):
        """Test filtering characters by those assaigned to series"""
        character1 = Character.objects.create(
            user=self.user, name='Abegille Mac'
        )
        character2 = Character.objects.create(
            user=self.user, name="Andy Christopher"
        )
        series = Series.objects.create(
            title="Tom & Jerry",
            status=False,
            watch_rate=4,
            rating=9.00,
            user=self.user
        )
        series.characters.add(character1)
        res = self.client.get(CHARACTERS_URL, {'assigned_only': 1})

        serializer1 = CharacterSerializer(character1)
        serializer2 = CharacterSerializer(character2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    # TEST &:- uniqness of characters
    def test_retrieve_characters_assigned_unique(self):
        """Test filtering characters by assigned return unique items"""
        character = Character.objects.create(user=self.user, name="Magneto")
        Character.objects.create(user=self.user, name="Wolverine")

        series1 = Series.objects.create(
            title="X-men origins",
            status=False,
            watch_rate=4,
            rating=7.8,
            user=self.user
        )
        series1.characters.add(character)
        series2 = Series.objects.create(
            title="Bunny Golf",
            status=True,
            watch_rate=9,
            rating=10,
            user=self.user
        )
        series2.characters.add(character)

        res = self.client.get(CHARACTERS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
