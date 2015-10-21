from rest_framework import serializers

from puser.models import PUser


class UserSerializer(serializers.ModelSerializer):
    profile_link = serializers.CharField(source='get_absolute_url', read_only=True)
    picture = serializers.CharField(source='picture_link', read_only=True)
    display_name = serializers.CharField(source='get_full_name', read_only=True)
    registered = serializers.BooleanField(source='is_registered', read_only=True)

    class Meta:
        model = PUser
        fields = ('id', 'username', 'first_name', 'last_name', 'profile_link', 'picture', 'display_name', 'registered')