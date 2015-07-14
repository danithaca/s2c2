from django.conf.urls import patterns, url
from circle import views

urlpatterns = patterns(
    "",
    url(r"^manage/personal$", views.ManagePersonal.as_view(), name="manage_personal"),
    url(r"^manage/public$", views.ManagePublic.as_view(), name="manage_public"),
)
