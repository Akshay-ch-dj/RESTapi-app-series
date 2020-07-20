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
        # lists the Characters with their id, detailed list will be created
        # later, to specify each of its name other ID
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


# Adding SeriesDetailSerializer(modified version of SeriesSerializer(inherit))
# Detail view specifies the tags and characters added to that series
class SeriesDetailSerializer(SeriesSerializer):
    """
    Serialize a series detail
    """
    # Django RF allows nesting serializers, as like these, many=can have many
    # characters associated with a series.
    characters = CharacterSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


# Adding Serializer to process the image uploaded
class SeriesImageSerializer(serializers.ModelSerializer):
    """
    serializer for uploading images to series
    """
    class Meta:
        model = Series
        fields = ('id', 'image')
        read_only_fields = ('id',)
