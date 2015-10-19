from django.conf.urls import patterns, url

from circle import views, models

urlpatterns = patterns(
    "",
    url(r"^parent/$", views.ParentCircleView.as_view(), name="parent"),
    url(r"^sitter/$", views.SitterCircleView.as_view(), name="sitter"),

    url(r"^group/$", views.TagCircleUserView.as_view(), name="tag"),
    url(r"^group/add/$", views.TagAddView.as_view(), name="tag_add"),
    url(r"^group/(?P<pk>\d+)/edit$", views.TagEditView.as_view(), name="tag_edit"),

    url(r"^user/(?P<uid>\d+)/$", views.UserConnectionView.as_view(), name="user_connection"),

    url(r"^group/(?P<pk>\d+)/$", views.CircleDetails.as_view(type_constraint=models.Circle.Type.TAG), name="tag_view"),
    url(r"^group/(?P<circle_id>\d+)/join/$", views.MembershipUpdateView.as_view(), name="membership_update"),
)
