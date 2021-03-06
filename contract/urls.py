from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy

from contract import views

urlpatterns = patterns(
    "",
    url(r'^(?P<pk>\d+)/$', views.ContractDetail.as_view(), name='view'),
    url(r"^$", views.EngagementList.as_view(), name="engagement_list"),
    url(r"^calendar/$", views.CalendarView.as_view(), name="calendar"),
    url(r"^(?P<pk>\d+)/edit/$", views.ContractEdit.as_view(), name="edit"),

    # post contract
    url(r"^post/favor/$", views.ContractCreateParentView.as_view(), name="add"),
    url(r"^post/favor/$", views.ContractCreateParentView.as_view(), name="post_parent"),
    url(r"^post/paid/$", views.ContractCreateSitterView.as_view(), name="post_sitter"),
    url(r"^post/offer/$", views.ContractCreateOfferView.as_view(), name="post_offer"),

    url(r'^response/(?P<pk>\d+)/$', views.MatchDetail.as_view(), name='match_view'),
    # url(r'^match/(?P<pk>\d+)/edit/$', views.MatchDetail.as_view(edit=True), name='match_edit'),

    # only available for staff members to see all contracts.
    # url(r"^$", staff_member_required(views.ContractList.as_view(), login_url=reverse_lazy('account_login')), name="list"),

    # api related
    url(r'^(?P<pk>\d+)/status$', views.ContractChangeStatus.as_view(), name='change_status'),
    url(r'^response/(?P<pk>\d+)/accept/$', views.MatchStatusChange.as_view(switch=True), name='match_accept'),
    url(r'^response/(?P<pk>\d+)/decline/$', views.MatchStatusChange.as_view(switch=False), name='match_decline'),
    url(r'^api/my_list/$', views.APIMyEngagementList.as_view(), name='my_list'),
    url(r'^api/preview_query/$', views.ContractPreviewQuery.as_view(), name='preview_query'),
    url(r"^(?P<pk>\d+)/match_add/$", views.MatchAdd.as_view(), name="match_add"),        # to make it clear, let's use "activate" instead of "add"
)
