from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from user.models import UserProfile


@login_required
def staff_date(request, uid=None):
    user_profile = UserProfile.get_by_id_default(uid, request.user)
    return TemplateResponse(request, template='slot/staff.jinja2', context={
        'user_profile': user_profile
    })