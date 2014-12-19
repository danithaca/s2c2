from django.conf.urls import patterns, url
# from user.views import SignupView
from django.core.urlresolvers import reverse_lazy

urlpatterns = patterns(
    '',
    url(r'^login/$', 'user.views.login', name='login'),
    url(r'^logout/$', 'user.views.logout', name='logout'),
    url(r'^signup/$', 'user.views.signup', name='signup'),
    url(r'^edit/$', 'user.views.edit', name='edit'),

    # url(r'^password/change/$', 'django.contrib.auth.views.password_change', {
    #     'template_name': 'user/password_change.jinja2',
    #     'post_change_redirect': '/'
    # }, name='password_change'),

    # url(r'^password/reset/$', 'django.contrib.auth.views.password_reset', {
    #     'template_name': 'user/password_reset.jinja2',
    #     'post_reset_redirect': reverse_lazy('user:login')
    # }, name='password_reset'),
    url(r'^password/reset/$', 'user.views.password_reset', name='password_reset'),
    url(r'^password/reset/(?P<uidb64>\w+)/(?P<token>\w+)/$', 'user.views.password_reset_confirm', name='password_reset_confirm'),

    # url(r'^edit/(?P<user_id>\d*)/$', 'user.views.edit', name='edit'),
    # url(r'^signup/$', SignupView.as_view(), name='signup'),
)
