from django.conf.urls import patterns, url

from circle import views

urlpatterns = patterns(
    "",
    url(r"^parent/$", views.ParentCircleView.as_view(), name="parent"),
    url(r"^sitter/$", views.SitterCircleView.as_view(), name="sitter"),
    url(r"^group/$", views.TagCircleUserView.as_view(), name="tag"),
    url(r"^group/add/$", views.TagAddView.as_view(), name="tag_add"),
    url(r"^user/(?P<uid>\d+)/$", views.UserConnectionView.as_view(), name="user_connection"),
)
