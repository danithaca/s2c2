from django.conf.urls import patterns, url

from circle import views, models

urlpatterns = patterns(
    "",
    url(r"^parent/$", views.ParentManageView.as_view(), name="parent"),
    url(r"^sitter/$", views.SitterManageView.as_view(), name="sitter"),
    url(r"^group/$", views.GroupDirectoryView.as_view(), name="group"),

    url(r"^group/(?P<pk>\d+)/$", views.CircleDetails.as_view(type_constraint=models.Circle.Type.PUBLIC), name="group_view"),
    url(r"^group/add/$", views.GroupCreateView.as_view(), name="group_add"),
    url(r"^group/(?P<pk>\d+)/edit$", views.TagEditView.as_view(), name="tag_edit"),

    url(r"^user/(?P<uid>\d+)/$", views.UserConnectionView.as_view(), name="user_connection"),

    url(r"^group/(?P<circle_id>\d+)/join/$", views.MembershipUpdateView.as_view(), name="membership_update"),

    url(r"^membership/(?P<pk>\d+)/edit/$", views.MembershipEditView.as_view(), name="membership_edit"),
    url(r"^parent/(?P<pk>\d+)/edit/$", views.MembershipEditView.as_view(), name="membership_edit_parent"),
    url(r"^sitter/(?P<pk>\d+)/edit/$", views.MembershipEditView.as_view(), name="membership_edit_sitter"),

    # api related
    url(r"^membership/(?P<pk>\d+)/deactivate/$", views.DeactivateMembership.as_view(), name="membership_deactivate"),
    url(r"^(?P<pk>\d+)/activate/$", views.ActivateMembership.as_view(), name="membership_activate"),        # to make it clear, let's use "activate" instead of "add"
)
