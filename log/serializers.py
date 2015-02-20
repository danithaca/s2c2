from rest_framework import serializers
from log import models


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Log
        fields = ('creator', 'type', 'ref', 'message', 'updated')