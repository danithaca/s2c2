import logging
import traceback
from django import template
from django.contrib.auth.models import User
from django.template.defaultfilters import truncatechars, urlencode
from django.templatetags.static import static
from django.templatetags.tz import utc
from image_cropping.templatetags.cropping import cropped_thumbnail
from sitetree.templatetags.sitetree import SimpleNode, sitetree

from contract.models import Engagement
from p2.utils import get_site_url, TrustedMixin, TrustLevel
from puser.models import PUser

register = template.Library()


@register.filter
def bootstrap_alert(message):
    try:
        sub = message.level_tag if message.level_tag != 'error' else 'danger'
        return 'alert-%s' % sub
    except Exception:
        return ''


@register.simple_tag(takes_context=True)
def user_picture_url(context, puser, **kwargs):
    assert isinstance(puser, User), 'Wrong type: %s' % type(puser)
    puser = PUser.from_user(puser)
    if puser.has_picture():
        try:
            return cropped_thumbnail(context, puser.info, 'picture_cropping',upscale=True, **kwargs)
        except Exception as e:
            traceback.print_exc()
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
    assert isinstance(user, User), 'Type is %s' % type(user)
    name = user.first_name or user.last_name or user.username
    return truncatechars(name, 12)


@register.simple_tag(name='user-full-name')
def p2_tag_user_full_name(user):
    assert isinstance(user, User), 'Type is: %s' % type(user)
    return user.get_full_name() or user.username


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


@register.simple_tag(name='gcal-url')
def p2_tag_gcal_url(engagement):
    assert isinstance(engagement, Engagement), 'Type is: %s' % type(engagement)
    url_template = "https://www.google.com/calendar/render?action=TEMPLATE&text={title}&dates={start}/{end}&details={details}&location&trp=false"
    convert = lambda t: utc(t).strftime('%Y%m%dT%H%M%SZ')
    start, end = convert(engagement.contract.event_start), convert(engagement.contract.event_end)
    url = url_template.format(
        title=urlencode('Babysitting (Servuno)'),
        start=str(start),
        end=str(end),
        details=urlencode(get_site_url() + engagement.get_link())
    )
    return url


# @register.simple_tag(name='engagement_time')
# def p2_tag_engagement_time(engagement):
#     assert isinstance(engagement, Engagement), 'Type is: %s' % type(engagement)
#     return ''


# @register.simple_tag(name='current-menutree-dropdown', takes_context=True)
# def p2_tag_menutree_dropdown(context):
#     sitetree = get_sitetree()
#     tree_item = sitetree.get_tree_current_item('main')
#     navigation_type = 'menu'
#     use_template = 'sitetree/breadcrumbs_dropdown.html'
#     return sitetree.children(tree_item, navigation_type, use_template, context)


@register.tag
def menutree_dropdown(parser, token):
    """Renders a title for current page, resolved against sitetree item representing current URL."""
    return menutree_dropdownNode.for_tag(parser, token, 'from', 'menutree_dropdown from "mytree"')


class menutree_dropdownNode(SimpleNode):
    """Renders a page description from the specified site tree."""

    def get_value(self, context):
        current_item = sitetree.get_tree_current_item(self.item)
        navigation_type = 'tree'
        use_template = 'sitetree/breadcrumbs_dropdown.html'
        return sitetree.children(current_item, navigation_type, use_template, context)


@register.assignment_tag(takes_context=True, name='is-trusted')
def p2_tag_current_user_trusted(context, object, level):
    assert object is not None and isinstance(object, TrustedMixin)
    user = context.get('current_user', None)
    if user is None:
        user = context.get('user', None)
    assert user is not None

    mapping = {e.name.lower(): e.value for e in list(TrustLevel)}
    level = mapping.get(level.strip().lower())
    if level is None:
        level = int(level)

    return object.is_user_trusted(user, level)