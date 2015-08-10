from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from image_cropping import ImageCroppingMixin
from puser.models import Info


class UserInfoAdmin(UserAdmin):
    class InfoInline(ImageCroppingMixin, admin.StackedInline):
        model = Info
        can_delete = False
        verbose_name_plural = 'info'

    inlines = (InfoInline, )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name'),
        }),
    )

    def full_name(self, user):
        return user.get_full_name()
    full_name.short_description = 'Name'

    class MissingInfoFilter(SimpleListFilter):
        title = 'missing info'
        parameter_name = 'missing'

        def lookups(self, request, model_admin):
            return (
                ('missing', 'missing'),
            )

        def queryset(self, request, queryset):
            if self.value() == 'missing':
                return queryset.filter(info__isnull=True)

    list_filter = UserAdmin.list_filter + (MissingInfoFilter, )
    list_display = UserAdmin.list_display + ('date_joined', 'last_login')
    ordering = ('-date_joined', '-last_login')

# Re-register UserAdmin, GroupAdmin
admin.site.unregister(User)
admin.site.register(User, UserInfoAdmin)