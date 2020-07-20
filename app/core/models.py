import uuid
import os

from django.db import models
# The base classes need to use when customizing or overriding Django User model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.conf import settings
# To add timezone based on settings UTC
from django.utils import timezone


# To add images to api, helper function, instance-creates the path
def series_image_file_path(instance, filename):
    """Generate File path for new series file"""
    # Strip out the extension part of the file name
    ext = filename.split('.')[-1]
    # Creates a file with a random uuid and same extension.
    filename = f"{uuid.uuid4()}.{ext}"

    return os.path.join('uploads/series/', filename)


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

    # Assign the 'UserManager' to the 'objects'(inbuilt class attr- modified)
    objects = UserManager()

    # Need a username field, changed the username field to email field
    USERNAME_FIELD = 'email'

    # IMP: Every model needs a string representation
    def __str__(self):
        """Return String Representation of the user( by email address)"""
        return self.email


# For the series app 'Tag' model
class Tag(models.Model):
    """
    Tag to attach to the series
    """
    name = models.CharField(max_length=255)
    # user-> foreign key to 'User' object-but not address it directly instead
    # use the 'AUTH_USER-MODEL' from the django settings
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """String representation of Tag model"""
        return self.name


# For the series app 'Character' model
class Character(models.Model):
    """
    Characters in the series
    """
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """String representation of Character model"""
        return self.name


# Real Series MODEL
class Series(models.Model):
    """
    Series object
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    start_date = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=False)
    watch_rate = models.IntegerField()
    rating = models.DecimalField(max_digits=4, decimal_places=2)
    # Use 'blank=True' to make CharField object optional
    link = models.CharField(max_length=255, blank=True)
    # The tags and Characters can be add as many-to-many relationships
    characters = models.ManyToManyField('Character')
    tags = models.ManyToManyField('Tag')
    # Add the ImageField, pass reference to the function
    Image = models.ImageField(null=True, upload_to=series_image_file_path)

    def __str__(self):
        return self.title
