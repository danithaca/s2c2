from django.conf.urls import patterns, url
from contract import views

urlpatterns = patterns(
    "",
    url(r'^(?P<pk>\d+)/$', views.ContractDetail.as_view(), name='view'),
    url(r"^add/$", views.ContractCreate.as_view(), name="add"),
)
