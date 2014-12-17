from django.conf.urls import patterns, url
# from user.views import SignupView

urlpatterns = patterns(
    '',
    url(r'^login/$', 'user.views.login', name='login'),
    url(r'^logout/$', 'user.views.logout', name='logout'),
    url(r'^signup/$', 'user.views.signup', name='signup'),
    # url(r'^signup/$', SignupView.as_view(), name='signup'),
)
