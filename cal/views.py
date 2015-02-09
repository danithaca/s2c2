from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.template.response import TemplateResponse
from s2c2.decorators import user_check_against_arg
from user.models import UserProfile


# permission: myself or verified user from same center.
@login_required
@user_check_against_arg(
    lambda view_user_profile, target_user: target_user is None or view_user_profile.user == target_user or view_user_profile.is_verified() and view_user_profile.is_same_center( target_user),
    lambda args, kwargs: get_object_or_404(User, pk=kwargs['uid']) if 'uid' in kwargs and kwargs['uid'] is not None else None,
    lambda u: UserProfile(u)
)
def calendar_staff(request, uid=None):
    user_profile = UserProfile.get_by_id_default(uid, request.user)
    context = {
        'user_profile': user_profile,
        }
    return TemplateResponse(request, template='cal/staff.html', context=context)