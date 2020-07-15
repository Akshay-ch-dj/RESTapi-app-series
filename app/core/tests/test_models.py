from django.test import TestCase
# Test the model can create a new user, from the user function
# Instead of importing the model directly(not recommended)..import it from
# settings so that - models only need to change there only.
from django.contrib.auth import get_user_model

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

    # Test to add new model Character(same as test_tag_str)
    def test_Character_str(self):
        """Test the Character string representation"""
        # Sample
        character = models.Character.objects.create(
            user=sample_user(),
            name='James Cole'
        )
        self.assertEqual(str(character), character.name)
