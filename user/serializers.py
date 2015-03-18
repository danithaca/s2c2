from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    profile_link = serializers.CharField(source='get_link', read_only=True)
    picture = serializers.CharField(source='user_profile.picture_link', read_only=True)
    display_name = serializers.CharField(source='get_name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'profile_link', 'picture', 'display_name')