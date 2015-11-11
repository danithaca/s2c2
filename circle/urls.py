from django.conf.urls import patterns, url

from circle import views, models
from p2.utils import UserRole

urlpatterns = patterns(
    "",
    # url(r"^parent/$", views.ParentCircleView.as_view(), name="parent"),
    url(r"^parent/$", views.ParentCircleManageView.as_view(), name="parent"),
    # url(r"^sitter/$", views.SitterCircleView.as_view(), name="sitter"),
    url(r"^sitter/$", views.SitterCircleManageView.as_view(), name="sitter"),

    url(r"^view/$", views.ListMembersView.as_view(), name="list_network"),

    url(r"^sitter/pool/$", views.SitterPoolView.as_view(), name="sitter_pool"),
    url(r"^parent/pool/$", views.ParentPoolView.as_view(), name="parent_pool"),

    url(r"^group/$", views.TagCircleUserView.as_view(), name="tag"),
    url(r"^group/add/$", views.TagAddView.as_view(), name="tag_add"),
    url(r"^group/(?P<pk>\d+)/edit$", views.TagEditView.as_view(), name="tag_edit"),

    url(r"^user/(?P<uid>\d+)/$", views.UserConnectionView.as_view(), name="user_connection"),

    url(r"^group/(?P<pk>\d+)/$", views.CircleDetails.as_view(type_constraint=models.Circle.Type.TAG), name="tag_view"),
    url(r"^group/(?P<circle_id>\d+)/join/$", views.MembershipUpdateView.as_view(), name="membership_update"),

    url(r"^membership/(?P<pk>\d+)/edit/$", views.MembershipEditView.as_view(), name="membership_edit"),
    url(r"^parent/(?P<pk>\d+)/edit/$", views.MembershipEditView.as_view(), name="membership_edit_parent"),
    url(r"^sitter/(?P<pk>\d+)/edit/$", views.MembershipEditView.as_view(), name="membership_edit_sitter"),

    # api related
    url(r"^membership/(?P<pk>\d+)/deactivate/$", views.DeactivateMembership.as_view(), name="membership_deactivate"),
    url(r"^(?P<pk>\d+)/activate/$", views.ActivateMembership.as_view(), name="membership_activate"),        # to make it clear, let's use "activate" instead of "add"
)
