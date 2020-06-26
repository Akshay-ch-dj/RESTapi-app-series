from django.db import models
# The base classes need to use when customizing or overriding Django User model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin

# Custom manager-default django behaviour changed, usname replaced with Email


class UserManager(BaseUserManager):
    """
    Manager for User profiles
    """
    # Add any additional fields to 'extra_fields'- ad hoc
    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError("User must have an email address")
        # Normalize the email address,(lowercase the second half of the email)
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # to ensure password is hashed
        user.set_password(password)
        user.save(using=self._db)

        return user

    # All superusers need password, to create a superuser
    def create_superuser(self, email, password):
        """Create and save a new superuser with given details"""
        # Class(self) automatically passed in when a fun. calls
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


# customizing the django default user model, need to configure in settings.py
# Before the first migrate, put:- "AUTH_USER_MODEL = 'core.User'"
class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model that uses 'email' instead of 'username'
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    # By default-activated, but can deactivated
    is_active = models.BooleanField(default=True)
    # By default no one is a staff
    is_staff = models.BooleanField(default=False)

    # Assign the 'UserManager' to the 'objects'
    objects = UserManager()

    # Need a username field, changed the username field to email field
    USERNAME_FIELD = 'email'

    # IMP: Every model needs a string representation
    def __str__(self):
        """Return String Representation of the user( by email address)"""
        return self.email
