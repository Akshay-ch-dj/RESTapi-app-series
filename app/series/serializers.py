from rest_framework import serializers

from core.models import Tag, Character, Series


# Creating a ModelSerializer and link to Tag MODEL, pull in ID and name values
class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag objects
    """

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class CharacterSerializer(serializers.ModelSerializer):
    """
    Serializer for Character objects
    """

    class Meta:
        model = Character
        fields = ('id', 'name')
        read_only_fields = ('id',)


class SeriesSerializer(serializers.ModelSerializer):
    """
    Serialize a Series object
    """
    characters = serializers.PrimaryKeyRelatedField(
        many=True,
        # This lists the Characters with their id,
        queryset=Character.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Series
        fields = (
            'id', 'title', 'characters', 'tags', 'start_date',
            'status', 'rating', 'link', 'watch_rate'
        )
        read_only_fields = ('id', 'start_date')
        # The 'Characters' and 'Tags' are seperate models, so need to add them
        # as special fields |^|
