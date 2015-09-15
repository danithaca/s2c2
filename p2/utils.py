from django.shortcuts import redirect

# import only in method in order to avoid circular import


################# mixin ####################

class UserOnboardRequiredMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if not request.puser.has_area():
            return redirect('onboard_start')
        return super().dispatch(request, *args, **kwargs)