from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.utils.decorators import available_attrs
from user.models import UserProfile


# this version uses user_passes_test(), which redirect to LOGIN_URL, which is not desirable
# def user_is_verified(function=None):
#     def test_user_verified(user):
#         user_profile = UserProfile(user)
#         return user_profile.is_verified()
#
#     actual_decorator = user_passes_test(
#         test_user_verified,
#     )
#     if function:
#         return actual_decorator(function)
#     return actual_decorator


# def user_is_verified(function):
#     """ A decorator that redirects to "user:edit" if not verified and show a warning message."""
#     def decorator(view_func):
#
#         @wraps(view_func, assigned=available_attrs(view_func))
#         def _wrapped_view(request, *args, **kwargs):
#             # test verification here.
#             if UserProfile(request.user).is_verified():
#                 return view_func(request, *args, **kwargs)
#             # if user is not verified, redirect to 'user:edit'.
#             messages.error(request, 'This operation requires your user account to be verified. Please fill in necessary information about yourself and ask your manager to verify your account.')
#             return redirect('user:edit')
#             # this is the end of _wrapped_view()
#
#         # return @wraps(_wrapped_view()) from decorator()
#         return _wrapped_view
#
#     # return decorator() as the real decorator.
#     return decorator(function)


def user_is_verified(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # test verification here.
        if UserProfile(request.user).is_verified():
            return view_func(request, *args, **kwargs)
        # if user is not verified, redirect to 'user:edit'.
        messages.error(request, 'This operation requires your user account to be verified. Please fill in necessary information about yourself and ask your manager to verify your account.')
        return redirect('user:edit')
        # this is the end of _wrapped_view()

    return _wrapped_view