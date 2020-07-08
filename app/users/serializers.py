from django.contrib.auth import get_user_model, authenticate
# language translation system used in python strings
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


# using model serializer
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the user object
    """

    class Meta:
        model = get_user_model()
        # The fields need to be converted <=> JSON,(when http_post) save to db
        fields = ('email', 'password', 'name')
        # Extra settings, ensure the password is write only and min. length '5'
        extra_kwargs = {'password':
                        {'write_only': True,
                            'min_length': 5,
                            'style': {'input_type': 'password'}
                         }
                        }

    # Override the 'create' function
    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        # use the 'create_user' Manager function, validated_data contains all
        # data ie, passed into the serializer(json) --> python dict.-kwargs
        return get_user_model().objects.create_user(**validated_data)


# After failing tests_users_api token generation tests(4,5,6 and 7)
class AuthTokenSerializer(serializers.Serializer):
    """
    serializer for the user authentiacation object
    """
    # 'django-authenticate' fn. helper command-> automatically authenticate usr
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    # Validate function- to check inputs are all correct, TokenSerializer
    def validate(self, attrs):
        """Validate and authenticate the user"""
        # attrs get passed in as dictionary
        email = attrs.get('email')
        password = attrs.get('password')

        # Access the context of the request ie. made
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            # authentiacation fails or did'nt return the user
            msg = _('Unable to authenticate with provided credentials')
            # raises error, Django RF handles the error by passing it as a
            # 400_response ---> sent it to user
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        # Whenever overriding a validation function(attrs)-must return it last
        return attrs
