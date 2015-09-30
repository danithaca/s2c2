from django.conf.urls import patterns, url
from circle import views

urlpatterns = patterns(
    "",
    url(r"^manage/personal/$", views.ManagePersonal.as_view(), name="manage"),      # this is the default link
    url(r"^manage/personal/$", views.ManagePersonal.as_view(), name="manage_personal"),
    url(r"^manage/public/$", views.ManagePublic.as_view(), name="manage_public"),
    url(r"^manage/agency/$", views.ManageAgency.as_view(), name="manage_agency"),
    url(r"^manage/loop/", views.ManageLoop.as_view(), name="manage_loop"),

    url(r"^parent/$", views.ParentCircleView.as_view(), name="parent"),

)
