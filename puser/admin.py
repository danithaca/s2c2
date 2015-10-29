from account.models import Account, EmailAddress
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from image_cropping import ImageCroppingMixin
from django.utils.translation import ugettext_lazy as _
from sitetree.admin import TreeItemAdmin, override_item_admin

from login_token.models import Token
from puser.models import Info, Area


class UserInfoAdmin(UserAdmin):
    class InfoInline(ImageCroppingMixin, admin.StackedInline):
        model = Info
        can_delete = False
        verbose_name_plural = 'info'

    class TokenInline(admin.StackedInline):
        model = Token
        can_delete = True

    class AccountInline(admin.StackedInline):
        model = Account
        can_delete = True

    class EmailAddressInline(admin.StackedInline):
        model = EmailAddress
        can_delete = True
        extra = 0

    inlines = (InfoInline, TokenInline, EmailAddressInline, AccountInline)

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
# admin.site.register(PUser, UserInfoAdmin)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', )


class MenuItemAdmin(TreeItemAdmin):
    fieldsets = (
        (_('Basic settings'), {
            'fields': ('parent', 'title', 'url', 'urlaspattern', 'hint', 'description', 'alias', 'fa_icon')
        }),
        (_('Access settings'), {
            # 'classes': ('collapse',),
            'fields': ('access_loggedin', 'access_guest', 'access_restricted', 'access_permissions', 'access_perm_type')
        }),
        (_('Display settings'), {
            #'classes': ('collapse',),
            'fields': ('hidden', 'inmenu', 'inbreadcrumbs', 'insitetree', 'importance')
        }),
    )


override_item_admin(MenuItemAdmin)
