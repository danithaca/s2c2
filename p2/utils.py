from django.contrib.sites.models import Site
from django.shortcuts import redirect

# import only in method in order to avoid circular import


################# mixin ####################

class UserOnboardRequiredMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if not request.puser.has_area():
            return redirect('onboard_start')
        return super().dispatch(request, *args, **kwargs)


def get_site_url():
    current_site = Site.objects.get_current()
    return 'http://%s' % current_site.domain