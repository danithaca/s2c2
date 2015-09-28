from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.contrib import admin
from p2 import settings, views
from s2c2 import utils


urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),
    url(r'^help/$', views.HelpView.as_view(), name='help'),
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    url(r'^landing/$', views.LandingView.as_view(), name='landing'),

    url(r'^dashboard/$', views.DashboardView.as_view(), name='dashboard'),

    # first occurance takes priority
    url(r"^account/", include("puser.urls")),
    url(r'^account/', include('account.urls')),
    #url(r"^user/", include("puser.urls", namespace='user')),

    url(r'^circle/', include('circle.urls', namespace='circle')),
    url(r'^contract/', include('contract.urls', namespace='contract')),
    url(r'^shout/', include('shout.urls', namespace='shout')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^dummy/$', utils.dummy, name='dummy'),
    url(r'^experiment/$', views.ExperimentView.as_view(), name='experiment'),

    # note: the following thing about static is only valid in dev.
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
