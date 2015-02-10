from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import available_attrs
from django.views import defaults
from django.views.defaults import bad_request
from location.models import Classroom
from user.models import UserProfile


def user_is_verified(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # test verification here.
        if not request.user.is_superuser:
            if not UserProfile(request.user).is_verified():
                # messages.error(request, 'The operation requires your user account to be verified.')
                return defaults.permission_denied(request)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def user_is_center_manager(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            if not UserProfile(request.user).is_center_manager():
                # messages.error(request, 'The operation is only valid for center managers.')
                return defaults.permission_denied(request)
        return view_func(request, *args, **kwargs)      
    return _wrapped_view
    
    
# if the first_arg is positional, get_func==lambda x: x[0][0]
# if it's kwargs, get_func=lambda x: x[1]['arg']
def user_check_against_arg(check_func, get_func, request_user_func=lambda u: u):
    """ check_func returns True means test passed. Return False to redirect to 403. """
    def _wrapper_outer(view_func):
        @wraps(view_func)
        def _wrapper_inner(request, *args, **kwargs):
            if not request.user.is_superuser:
                if not check_func(request_user_func(request.user), get_func(args, kwargs)):
                    return defaults.permission_denied(request)
            return view_func(request, *args, **kwargs)
        return _wrapper_inner
    return _wrapper_outer


def user_is_me_or_same_center(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        return user_check_against_arg(
            lambda view_user_profile, target_user: target_user is None or view_user_profile.user == target_user or view_user_profile.is_verified() and view_user_profile.is_same_center(target_user),
            lambda args, kwargs: get_object_or_404(User, pk=kwargs['uid']) if 'uid' in kwargs and kwargs['uid'] is not None else None,
            lambda u: UserProfile(u)
        )(view_func)(request, *args, **kwargs)
    return _wrapped_view
    
    
# def user_is_same_center(convert_target_func):
#     @wraps(view_func)
#     def _wrapped_view(request, first_arg, *args, **kwargs):
#         if UserProfile(request.user).is_same_center(convert_target_func(first_arg))
#             return view_func(request, *args, **kwargs)
#         messages.error(request, 'This operation is only valid for center managers.')
#         return redirect('dashboard')
#     return _wrapped_view


def user_classroom_same_center(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_profile = UserProfile(request.user)
        classroom = get_object_or_404(Classroom, pk=kwargs['cid'])
        if not request.user.is_superuser:
            if not user_profile.is_same_center(classroom):
                # messages.error(request, 'The operation is only valid for center managers.')
                return defaults.permission_denied(request)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def is_ajax(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.is_ajax():
            return bad_request(request)
        return view_func(request, *args, **kwargs)
    return _wrapped_view