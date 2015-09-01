from account.models import SignupCode
from django import template
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.template.defaultfilters import truncatechars, urlencode
from django.templatetags.static import static
from image_cropping.templatetags.cropping import cropped_thumbnail
from contract.models import Contract, Match
from puser.models import PUser
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def user_picture_url(context, puser, **kwargs):
    assert isinstance(puser, User), 'Wrong type: %s' % type(puser)
    puser = PUser.from_user(puser)
    if puser.has_picture():
        try:
            return cropped_thumbnail(context, puser.info, 'picture_cropping',upscale=True, **kwargs)
        except:
            # todo: add logging info.
            pass
    return static('user_200x200.png')


# @register.simple_tag(name='formatted-user-name')
# def p2_tag_formatted_user_name(user):
#     if user.get_full_name():
#         return '<span class="formatted-user-name" data-pk="%d">%s<span>' % (user.id, user.get_full_name())
#     else:
#         return '<span class="formatted-user-name word-break" data-pk="%d">%s<span>' % (user.id, user.email)


# @register.simple_tag(name='count-serves')
# def p2_tag_count_serves(u1, u2):
#     pu1, pu2 = PUser.from_user(u1), PUser.from_user(u2)
#     return pu1.count_served(pu2)


@register.simple_tag(name='user-short-name')
def p2_tag_user_short_name(user):
    assert isinstance(user, User)
    name = user.first_name or user.last_name or user.username
    return truncatechars(name, 10)


@register.simple_tag(name='user-full-name')
def p2_tag_user_full_name(user):
    assert isinstance(user, User), 'Type is: %s' % type(user)
    return user.get_full_name() or user.email


# @register.simple_tag(name='user-signup-url')
# def p2_tag_user_signup_url(user):
#     assert isinstance(user, User) and not user.is_active
#     code = SignupCode.objects.filter(email=user.email).order_by('-id').first()
#     protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
#     current_site = Site.objects.get_current()
#     if code:
#         return "{0}://{1}{2}?{3}".format(
#             protocol,
#             current_site.domain,
#             reverse("account_signup"),
#             urlencode({"code": code.code})
#         )
#     else:
#         return "{0}://{1}{2}".format(
#             protocol,
#             current_site.domain,
#             reverse("account_signup")
#         )


@register.filter
def negate(value):
    return -value
