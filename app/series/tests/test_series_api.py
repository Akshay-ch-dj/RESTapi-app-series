from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Inbuilt python fun. to generate temp. files
import tempfile
import os

# Image library from Pillow
from PIL import Image

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Series, Tag, Character
from series.serializers import SeriesSerializer, SeriesDetailSerializer


# Variable for series url
SERIES_URL = reverse('series:series-list')


# To generate the upload image URL
def image_upload_url(series_id):
    """Return URL for series image upload"""
    return reverse('series:series-upload-image', args=[series_id])


# for detail api, need a url with idea
# /api/series/serieses/1, need to pass in this argument(id), at the time of
# creating url, a function for generating series url.
def detail_url(series_id):
    """Returns Series detail URL"""
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

    # Tests for creates series using API
    # tests-for basic series, with tags assigned & characters assigned.
    # TEST 5
    def test_create_basic_series(self):
        """Test creating series"""
        payload = {
            'title': '12 monkeys',
            'status': True,
            'watch_rate': 5,
            'rating': 8.50
        }
        res = self.client.post(SERIES_URL, payload)
        # std. http response code for creating objects.
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # when an object is created in DRF it returnes a dictionary with
        # created object, it is used to get the 'id' of created object.
        series = Series.objects.get(id=res.data['id'])
        # check each keys-assigned correctly-use 'getattr'-for api obj. key
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(series, key))

    # TEST 6:- creating a series with tags assigned, pass in a list of tag
    # id's when creating the series
    def test_create_series_with_tags(self):
        """Test creating a series with tags"""
        tag1 = sample_tag(user=self.user, name='Sci-Fi')
        tag2 = sample_tag(user=self.user, name='18+')
        payload = {
            'title': 'How I Met Your Mother',
            'tags': [tag1.id, tag2.id],
            'status': False,
            'watch_rate': 3,
            'rating': 5.00
        }
        res = self.client.post(SERIES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        series = Series.objects.get(id=res.data['id'])
        # Need to retrive the tags created
        tags = series.tags.all()
        # check the no. of tags is '2'
        self.assertEqual(tags.count(), 2)
        # check the tags are same, 'assertIn' checks in lists, querysets
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    # TEST 7:- for series with characters
    def test_create_series_with_characters(self):
        """Test to create series with characters"""
        character1 = sample_character(user=self.user, name='James Cole')
        character2 = sample_character(user=self.user, name='The Witness')

        payload = {
            'title': '12 monkeys',
            'characters': [character1.id, character2.id],
            'status': True,
            'watch_rate': 5,
            'rating': 8.00
        }
        res = self.client.post(SERIES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        series = Series.objects.get(id=res.data['id'])
        characters = series.characters.all()

        self.assertEqual(characters.count(), 2)
        self.assertIn(character1, characters)
        self.assertIn(character2, characters)

    # Testing the update series feature, partial and full update.
    # TEST 8:- patch
    def test_partial_update_series(self):
        """Test updating a series with patch"""
        series = sample_series(user=self.user)
        series.tags.add(sample_tag(user=self.user))

        # Replace the default tag with a new tag
        new_tag = sample_tag(user=self.user, name="mafia")

        payload = {
            'title': "The End of the Fu**ing World",
            'tags': [new_tag.id]
        }
        # use the detail url to do the patch
        url = detail_url(series.id)
        # patch request
        self.client.patch(url, payload)

        # retrieve the update to the series from the database, and check match.
        # refreshes the details in the series from the database., in python db-
        # changes wont get affect in the object unless "refresh_from_db".
        series.refresh_from_db()
        self.assertEqual(series.title, payload['title'])
        tags = series.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    # TEST 9:- FULL UPDATE
    def test_full_update_series(self):
        """Test updating a series with put"""
        series = sample_series(user=self.user)
        # Adding a default tag and character
        series.tags.add(sample_tag(user=self.user))
        series.characters.add(sample_character(user=self.user))

        # The new tag to be put
        new_tag = sample_tag(user=self.user, name="sitcom")

        # The payload
        payload = {
            'title': "The office",
            'status': False,
            'watch_rate': 3,
            'rating': 8.00,
            'tags': [new_tag.id]
        }
        # put request
        url = detail_url(series.id)
        self.client.put(url, payload)

        series.refresh_from_db()
        self.assertEqual(series.title, payload['title'])
        self.assertEqual(series.status, payload['status'])
        self.assertEqual(series.watch_rate, payload['watch_rate'])
        self.assertEqual(series.rating, payload['rating'])
        tags = series.tags.all()
        characters = series.characters.all()
        self.assertEqual(len(tags), 1)
        self.assertEqual(len(characters), 0)
        self.assertIn(new_tag, tags)


# New Test class for Image uploading functionality
class SeriesImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@akshay.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        # A sample series instance for uploading, add object in test setup cz
        # not need to manipulate one in image fn. testing(need readymade one)
        self.series = sample_series(user=self.user)

    # Before the test it runs setUp() fn, there is "tearDown()" which runs
    # After the test runs.[here it is to kept file sys. clean after test]
    def tearDown(self):
        """To delete the leftover files after the SeriesImageUploadTests"""
        self.series.image.delete()

    # Two tests one is to test image uploading, and uploadig an invalid one.
    # TEST 10:- image uploading
    def test_upload_image_to_series(self):
        """Test uploading an image to series"""
        url = image_upload_url(self.series.id)
        # need a context manager with the tempfile, to create a named tempfile
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            # Create an temp. image file, upload it through api, Assertions
            # Creates a 10px X 10px black square.
            img = Image.new('RGB', (10, 10))
            # ntf= the file to save it
            img.save(ntf, format='JPEG')
            # seek-> in the end after saving,need it reset to 0 to access file
            ntf.seek(0)
            # need a multipart form request(form with data), default:json
            res = self.client.post(url, {'image': ntf}, format='multipart')

        # Assertions
        self.series.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.series.image.path))

    # TEST 11:- Test uploading a bad image
    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.series.id)
        res = self.client.post(url, {'image': 'NOT IMAGE'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Tests to add filtering options
    # TEST 12:-
    def test_filter_series_by_tags(self):
        """Test Returning series objects with specific tags"""
        # create 3 series objects, 2 with tags,1 with no tags
        series1 = sample_series(user=self.user, title='Lost')
        series2 = sample_series(user=self.user, title='Fargo')
        tag1 = sample_tag(user=self.user, name='Post-Apocalypse')
        tag2 = sample_tag(user=self.user, name='crime-investigation')
        series1.tags.add(tag1)
        series2.tags.add(tag2)
        series3 = sample_series(user=self.user, title='Senfield')

        # Pass values need to get- as dictionary,
        # The way API works on filtering, pass the tags seperated by comma to
        # filter the tagged results
        res = self.client.get(
            SERIES_URL,
            {'tags': f"{tag1.id},{tag2.id}"}
        )
        # Serialize the series and check if they exists in the response.
        serializer1 = SeriesSerializer(series1)
        serializer2 = SeriesSerializer(series2)
        serializer3 = SeriesSerializer(series3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    # TEST 13:-
    def test_filter_series_by_characters(self):
        """Test returning series with specific characters"""
        series1 = sample_series(user=self.user, title="Twin Peakes")
        series2 = sample_series(user=self.user, title="Better call Saul")
        character1 = sample_character(user=self.user, name="Saul Goodman")
        character2 = sample_character(user=self.user, name="Laura Palmer")

        series1.characters.add(character1)
        series2.characters.add(character2)
        series3 = sample_series(user=self.user, title="Mr. Bean")

        res = self.client.get(
            SERIES_URL,
            {'characters': f"{character1.id},{character2.id}"}
        )

        serializer1 = SeriesSerializer(series1)
        serializer2 = SeriesSerializer(series2)
        serializer3 = SeriesSerializer(series3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
