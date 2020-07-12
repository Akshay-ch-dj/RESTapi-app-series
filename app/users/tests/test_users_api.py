from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# Rest framework test helper tools, APIClient: helps make and check requests
from rest_framework.test import APIClient
# status- module contains status codes, helps tests more readable&understand
from rest_framework import status

# Adding a constant variable in url for testing,
CREATE_USER_URL = reverse('users:create')
# url for token tests, http_post requests
TOKEN_URL = reverse('users:token')
# manage user endpoints url,
ME_URL = reverse('users:me')


# Helper function to create users for the tests(insted of creating manually..)
# flexibilty in the fields a user have(**params)
def create_user(**params):
    """Create Sample Users"""
    # get_user_model() grab the custom 'User' model from settings, using manag.
    # 'UserManager'(objects)--> passes arguments
    return get_user_model().objects.create_user(**params)


# Private and Public APIs, fn. like 'create_user' gonna be a Public API, used
# by new users, fns. like 'modify_user' are private..
# outsiders(unauthenticated) can't allowed to use that..
class PublicUserApiTests(TestCase):
    """
    Test the users API (public)
    """

    def setUp(self):
        self.client = APIClient()

    # Test1
    def test_create_valid_user_success(self):
        """Test Creating user with valid payload is succesfull"""
        # payload- is the object ie passed to API, when making request, here
        # testing they are correct and whether the user created successfully..
        payload = {
            'email': 'test@akshay.com',
            'password': 'testpassword',
            'name': 'Akshay'
        }
        # Making the request, does a http 'post' to the url for creating users
        res = self.client.post(CREATE_USER_URL, payload)
        # Expecting response: HTTP 201 created response(with help of RF-status)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # To check the user object is created or not, unwind the response(cz
        # the created user object returned in the API along with http 201)
        # the ret. response in format like dict.(like the payload with xtra id)
        user = get_user_model().objects.get(**res.data)
        # Assertions: checking password is correct
        self.assertTrue(user.check_password(payload['password']))
        # Security: password must not there be in returned data
        self.assertNotIn('password', res.data)

    # Test2
    def test_user_exists(self):
        """Tests, if anyone creates a user that already exists fails"""
        payload = {
            'email': 'test@akshay.com',
            'password': 'testpassword'
        }
        # creating user, payload will pass in as kwargs
        create_user(**payload)
        # recreating same user
        res = self.client.post(CREATE_USER_URL, payload)
        # Need a HTTP 400 bad request cz. the user exists already
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Test3: For learning
    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'test@akshay.com',
            'password': 'pwd'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Assure the user was never created, filter out the email
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()  # returns True/False
        self.assertFalse(user_exists)

    # In every test conducted, the DataBase gets refreshed-each test starts new
    # Test1 fails with: 'user' is not a registered namespace: NoreverseMatch
    # user url not specified(urls.py)

    # Test 4, the token generation tests are added to PublicUserApiTests
    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {'email': 'test@akshay.com', 'password': 'testpass'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        # need a http_200 response with a token in the data response,
        # check if there is a key-'token'
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # Test 5
    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email='test@shanku.com', password='testpass')
        payload = {'email': 'test@shanku.com', 'password': 'wrong'}
        # Expecting a HTTP_400_BAD_RESPONSE
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Test 6
    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        payload = {'email': 'test@akshay.com', 'password': 'testpass'}
        res = self.client.post(TOKEN_URL, payload)
        # No token: expecting HTTP_400_BAD_RESPONSE
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Test 7
    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 1, 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Test 8: -  Manage user Endpoints tests,
    # Test that authentication required for managing user endpoints,[[ IMP ]]
    def test_retrieve_user_unauthorized(self):
        """Test that authentication is requried for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# PRIVATE USER API TESTS :- Auth. required
# Adding some authenticated requests, to test the successful retrieval of
# profile, post is not allowed, patch, put supports(editing obj. allowed)
# also update the user using API,
class PrivateUserApiTests(TestCase):
    """
    Test API requests that require authentication
    """

    # Test 9: - To let authenticated before each test automatically
    def setUp(self):
        self.user = create_user(
            email='test@akshay.com',
            password='testpass',
            name='Akshay'
        )
        # client setUp
        self.client = APIClient()
        # Force authenticate requests, helper fn. simulte authenticated req.
        self.client.force_authenticate(user=self.user)

    # Test 10:- Test a succesfull profile retrieval of a logged in user
    def test_retrieve_profile_success(self):
        """Test retriving profile for logged in user"""
        res = self.client.get(ME_URL)
        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # test the returned result equal:- Expected- name & email.. No passw.
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    # Test 11:- Dont allow post requests
    def test_post_not_allowed(self):
        """Test that post is not allowed on the me url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Test 12:- allow authen. users to update profile using API
    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'Akshayc', 'password': 'newpassword'}

        res = self.client.patch(ME_URL, payload)

        # helper fn to update the user with the latest values from the database
        self.user.refresh_from_db()
        # Assertions
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
