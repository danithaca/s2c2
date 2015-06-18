from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from contract import views

urlpatterns = patterns(
    "",
    url(r'^(?P<pk>\d+)/$', login_required(views.ContractDetail.as_view()), name='view'),
    url(r"^add/$", login_required(views.ContractCreate.as_view()), name="add"),

    # only available for staff members to see all contracts.
    url(r"^$", staff_member_required(views.ContractList.as_view(), login_url=reverse_lazy('account_login')), name="list"),
)
