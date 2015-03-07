from rest_framework import serializers
from log import models
from user.serializers import UserSerializer


# todo: rename to CommentByLocationSerializer
class LogSerializer(serializers.ModelSerializer):
    # creator_user = UserSerializer(read_only=True)

    # note: source links to Model method, not serializer method.
    # creator_username = serializers.CharField(source='creator.username', read_only=True)
    creator_name = serializers.CharField(source='creator.get_name', read_only=True)
    creator_profile_link = serializers.CharField(source='creator.get_link', read_only=True)
    creator_picture = serializers.CharField(source='creator.user_profile.picture_link', read_only=True)

    class Meta:
        model = models.Log
        fields = ('id', 'creator', 'type', 'ref', 'message', 'updated', 'creator_name', 'creator_profile_link', 'creator_picture')

    # no need to override create() because it won't pass validation.
    # def create(self, validated_data):
    #     print(validated_data)
    #     pass

    # cid is not in kwargs. kwargs has the POST data, not views request kwargs data.
    # def __init__(self, *args, **kwargs):
    #     self.cid = kwargs.pop('cid', None)
    #     super(LogSerializer, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        request = self.context['request']
        cid = self.context['view'].kwargs['cid']
        new_data = {
            'message': data['message'],
            'type': models.Log.COMMENT_BY_LOCATION,
            'creator': request.user.id,
            'ref': '%s,%s' % (cid, data['day'])
        }
        return super(LogSerializer, self).to_internal_value(new_data)