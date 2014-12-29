# from user.models import UserProfile
#
#
# # see http://stackoverflow.com/questions/3006753/how-to-convert-request-user-into-a-proxy-auth-user-class
# class ConvertUserProfileMiddleware(object):
#     def process_request(self, request):
#         assert hasattr(request, 'user')
#         # request.user could be AnonymousUser
#         UserProfile.convert_user(request.user)