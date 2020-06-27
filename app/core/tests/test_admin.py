from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """
    Tests for the admin functions
    """

    #0) Setup Function, (sometimes there need to run setup tasks before test)
    def setUp(self):
        """Creating test client, setup for admin tests"""
        # A new User -logged in(ie. auth.), and another one- not authenticated
        # Assign the 'Client' class(imported) to new class(inherited) attribute
        self.client = Client()
        # authorized User
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@aksdev.com',
            password='password123'
        )
        # The 'client' helper fn. --> log in a user with Django authentication
        self.client.force_login(self.admin_user)

        # normal user
        self.user = get_user_model().objects.create_user(
            email='test@aksdev.com',
            password='password123',
            name='Test user full name'
        )

    # 1) TEST 1
    def test_users_listed(self):
        """Test to find users are listed in user page"""
        # reverse('app_name:the_url_identifier'), [#NOT YET CREATED]
        url = reverse('admin:core_user_changelist')
        # response= test client to perforn a 'HTTP' get on the url
        res = self.client.get(url)

        # Django custom assertion cheks the response contain the given item
        # Also checks internally that the HTTP - response is 200
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    # 2) TEST 2
    # further changes to django admin model
    def test_user_change_page(self):
        """Test that the user edit page works"""
        # The arguments passed gets added to url
        url = reverse('admin:core_user_change', args=[self.user.id])
        # like /admin/core/user/<id of user>
        res = self.client.get(url)

        # HTTP-200 page worked
        self.assertEqual(res.status_code, 200)

    # 3) TEST 3
    # To test the add page(Add User Page), adding new users in the Django
    def test_create_user_page(self):
        """Test to check the 'create user' page works"""
        # std url add page for the User model
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
