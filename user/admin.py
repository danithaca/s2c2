from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from user import models


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class ProfileInline(admin.StackedInline):
    model = models.Profile
    can_delete = False
    verbose_name_plural = 'profile'


# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (ProfileInline, )


# class RoleInline(admin.StackedInline):
#     model = models.Role
#     can_delete = False
#     verbose_name_plural = 'role'
#
#
# class RoleAdmin(GroupAdmin):
    # inlines = (RoleInline, )


# Re-register UserAdmin, GroupAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
# admin.site.register(Group, RoleAdmin)

admin.site.register(models.Role, GroupAdmin)

# register Staff
admin.site.register(models.Staff)


