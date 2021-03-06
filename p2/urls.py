from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.contrib import admin

from p2 import settings, views

urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),
    url(r'^help/$', views.HelpView.as_view(), name='help'),
    url(r'^tour/$', views.TourView.as_view(), name='tour'),
    url(r'^sitemap/$', views.SitemapView.as_view(), name='sitemap'),
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    url(r'^welcome/$', views.LandingView.as_view(), name='landing'),

    url(r'^dashboard/$', views.DashboardView.as_view(), name='dashboard'),

    # first occurance takes priority
    url(r"^account/", include("puser.urls")),
    url(r'^account/', include('account.urls')),
    #url(r"^user/", include("puser.urls", namespace='user')),

    url(r'^connect/', include('circle.urls', namespace='circle')),
    url(r'^job/', include('contract.urls', namespace='contract')),
    url(r'^message/', include('shout.urls', namespace='shout')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^experiment/$', views.ExperimentView.as_view(), name='experiment'),
    url(r'^logo/$', views.LogoView.as_view(), name='logo'),
    # url(r'^error/$', views.ErrorView.as_view(), name='error'),

    # note: the following thing about static is only valid in dev.
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
