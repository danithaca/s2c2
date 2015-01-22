from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group

from user import models
from user.models import UserProfile


class UserProfileAdmin(UserAdmin):
    class ProfileInline(admin.StackedInline):
        model = models.Profile
        can_delete = False
        verbose_name_plural = 'profile'

    inlines = (ProfileInline, )

    def full_name(self, user):
        return user.get_full_name()
    full_name.short_description = 'Name'

    def roles(self, user):
        if user.groups.exists():
            return ', '.join([g.role.machine_name if hasattr(g, 'role') else g.name for g in user.groups.all()])
        else:
            return '- None -'

    def verified(self, user):
        u = UserProfile(user)
        return u.is_verified()
    verified.boolean = True

    list_display = ('username', 'email', 'full_name', 'roles', 'verified', 'is_active', 'is_staff')

    class MissingProfileFilter(SimpleListFilter):
        title = 'missing profile'
        parameter_name = 'missing'

        def lookups(self, request, model_admin):
            return (
                ('missing', 'missing'),
            )

        def queryset(self, request, queryset):
            if self.value() == 'missing':
                return queryset.filter(profile__isnull=True)

    list_filter = UserAdmin.list_filter + (MissingProfileFilter, )


class GroupRoleAdmin(GroupAdmin):
    class RoleInline(admin.StackedInline):
        model = models.Role
        can_delete = False
        verbose_name_plural = 'role'

    inlines = (RoleInline, )

    def role_name(self, group):
        return group.role.machine_name if hasattr(group, 'role') else '- N/A -'
    role_name.short_description = 'machine name'

    list_display = ('name', 'role_name')

    class MissingRoleFilter(SimpleListFilter):
        title = 'missing role'
        parameter_name = 'missing'

        def lookups(self, request, model_admin):
            return (
                ('missing', 'missing'),
            )

        def queryset(self, request, queryset):
            if self.value() == 'missing':
                return queryset.filter(role__isnull=True)

    list_filter = GroupAdmin.list_filter + (MissingRoleFilter, )


# Re-register UserAdmin, GroupAdmin
admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
admin.site.unregister(Group)
admin.site.register(Group, GroupRoleAdmin)

# admin.site.register(models.Role, GroupAdmin)

# class FullUserAdmin(UserAdmin):
#     fieldsets = UserAdmin.fieldsets + (('Full user details', {'fields': ('address', 'phone_main', 'phone_backup', 'centers', 'validated')}), )

# register fulluser
# admin.site.register(models.FullUser, UserAdmin)
# admin.site.register(models.FullUser, FullUserAdmin)
# admin.site.register(models.Staff)


