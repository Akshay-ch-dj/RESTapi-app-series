from django.contrib.auth import get_user_model

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
