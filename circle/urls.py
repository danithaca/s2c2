from django.conf.urls import patterns, url

from circle import views, models

urlpatterns = patterns(
    "",
    # basic pages
    url(r"^list/$", views.DiscoverView.as_view(), name="discover"),
    url(r"^parent/$", views.ParentManageView.as_view(), name="parent"),
    url(r"^sitter/$", views.SitterManageView.as_view(), name="sitter"),
    url(r"^group/$", views.GroupDirectoryView.as_view(), name="group"),

    # group related
    url(r"^group/(?P<pk>\d+)/$", views.PublicCircleView.as_view(), name="group_view"),
    url(r"^group/add/$", views.GroupCreateView.as_view(), name="group_add"),
    url(r"^group/(?P<pk>\d+)/edit/$", views.GroupEditView.as_view(), name="group_edit"),
    url(r"^group/(?P<pk>\d+)/join/$", views.GroupJoinView.as_view(), name="group_join"),

    # url(r"^user/(?P<uid>\d+)/$", views.UserConnectionView.as_view(), name="user_connection"),
    url(r"^parent/add/(?P<uid>\d+)/$", views.ParentJoinView.as_view(), name="parent_add"),
    url(r"^sitter/add/(?P<uid>\d+)/$", views.SitterJoinView.as_view(), name="sitter_add"),

    # membership related
    url(r"^membership/(?P<pk>\d+)/edit/$", views.MembershipEditView.as_view(), name="membership_edit"),
    # url(r"^parent/list/(?P<pk>\d+)/edit/$", views.MembershipEditView.as_view(), name="membership_edit_parent"),
    # url(r"^sitter/list/(?P<pk>\d+)/edit/$", views.MembershipEditView.as_view(), name="membership_edit_sitter"),
    url(r"^group/list/(?P<pk>\d+)/edit/$", views.GroupMembershipEditView.as_view(), name="membership_edit_group"),
    url(r"^membership/(?P<pk>\d+)/approval/$", views.MembershipApprovalView.as_view(), name="approval"),

    # api related
    url(r"^membership/(?P<pk>\d+)/deactivate/$", views.DeactivateMembership.as_view(), name="membership_deactivate"),
    url(r"^membership/(?P<pk>\d+)/approve/$", views.ApproveMembership.as_view(), name="membership_approve"),
    url(r"^membership/(?P<pk>\d+)/disapprove/$", views.DisapproveMembership.as_view(), name="membership_disapprove"),
    url(r"^(?P<pk>\d+)/activate/$", views.ActivateMembership.as_view(), name="membership_activate"),        # to make it clear, let's use "activate" instead of "add"
)
