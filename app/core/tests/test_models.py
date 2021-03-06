from django.test import TestCase
# Test the model can create a new user, from the user function
# Instead of importing the model directly(not recommended)..import it from
# settings so that - models only need to change there only.
from django.contrib.auth import get_user_model
# Importing the patch decorator
from unittest.mock import patch

from core import models


# Helper function to create users (for series app)
def sample_user(email='test@akshaydev.com', password='testpass'):
    """Create a sample user"""
    # Basic user for testing the model(tag model)
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """
    To test the models
    """
    # 1) TEST 1
    def test_create_user_with_email_successfull(self):
        """Test creating a new user with email successful"""
        # pass in an 'email address' and 'password', verify the user is created
        # and the password is correct
        email = 'akshaych203@gmail.com'
        password = 'Testpass123'
        # 'create_user' fn. is called from 'UserManager' in the 'User' model
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        # Make assertions
        self.assertEqual(user.email, email)
        # can't check the password in the same way cz, encryption
        # use 'check_password'(inbuilt helper function) on the 'User' model
        self.assertTrue(user.check_password(password))

    # The first test will fail- it accepting the 'username'(std) field.
    # Project uses custom User model with 'email'

    # 2) TEST 2
    def test_new_user_email_normalaized(self):
        """Test the email for a new user is normalized"""
        email = 'test@AKSHAYDEV.COM'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    # 3) TEST 3
    def test_new_user_invalid_email(self):
        """Test if the user entered email is valid or not"""
        # Need a Value Error When No email is provided
        with self.assertRaises(ValueError):
            # Anything here should need to raise a value error, else test fail
            get_user_model().objects.create_user(None, 'test123')

    # 4) TEST 4
    # superuser got both is_staff and is_superuser
    def test_assure_superuser_created(self):
        """Test to ensure the superuser is created"""
        user = get_user_model().objects.create_superuser(
            'test@AKSHAYCH.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    # TEST 5
    # test to create a tag and verifies that it converts to the correct string
    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Action'
        )
        # to check the string representation of the model
        self.assertEqual(str(tag), tag.name)

    # TEST 6
    # Test to add new model Character(same as test_tag_str)
    def test_Character_str(self):
        """Test the Character string representation"""
        # Sample
        character = models.Character.objects.create(
            user=sample_user(),
            name='James Cole'
        )
        self.assertEqual(str(character), character.name)

    # TEST 7
    # Test to add a new model "Series" for creating series endpoints.
    def test_series_str(self):
        """Test the model "Series" string representation"""
        # There are required fields and optional fields, only req. fields
        # here out of series title(CharField), start_date(DatetimeField),
        # status[completed/not](BoolField), rating(of 10, DecimalField)
        # end_date,link(link to the official watch page of the series)
        # watch rate(episodes per week)--[IntegerField]
        # req fields:user, title, start_time(auto), status(compl./not), rating
        series = models.Series.objects.create(
            user=sample_user(),
            title='Game of Thrones',
            watch_rate=5,
            status=True,
            rating=8.98
        )
        self.assertEqual(str(series), series.title)

    # Adding model field for uploading image,
    # Always need to change the name of the uploaded file.To make sure all the
    # name are consistent and to avoid conflicts.
    # Add a function that will create a path to the image-and use a UUID, to
    # uniqu. identify the image[series_image_file_path()]
    # TEST 8:-Test image adding function, and use a UUID, to uniqually
    @patch('uuid.uuid4')
    def test_series_file_name_uuid(self, mock_uuid):
        """Test the image is saved in the correct location"""
        # Mock the default UID function, comes with UID library
        uuid = 'test-uuid'  # Any name
        # When uuid function gets called-change the def. value to return "uuid"
        mock_uuid.return_value = uuid
        # the parameters are:-instance(set to None), real file name(keep ext.)
        file_path = models.series_image_file_path(None, 'myimage.jpg')

        exp_path = f"uploads/series/{uuid}.jpg"
        self.assertEqual(file_path, exp_path)
