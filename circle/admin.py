from django.contrib import admin

from circle import models


@admin.register(models.Circle)
class CircleAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'owner', 'area')


@admin.register(models.SupersetRel)
class SupersetAdmin(admin.ModelAdmin):
    list_display = ('child', 'parent', 'created')


@admin.register(models.Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('member', 'circle', 'active', 'approved', 'type', 'created', 'updated')
    actions = ['approve_membership', 'disapprove_membership']

    def approve_membership(self, request, queryset):
        rows_updated = queryset.update(approved=True)
        if rows_updated == 1:
            message_bit = "1 membership was"
        else:
            message_bit = "%s memberships were" % rows_updated
        self.message_user(request, "%s successfully approved." % message_bit)

    def disapprove_membership(self, request, queryset):
        rows_updated = queryset.update(approved=False)
        if rows_updated == 1:
            message_bit = "1 membership was"
        else:
            message_bit = "%s memberships were" % rows_updated
        self.message_user(request, "%s successfully disapproved." % message_bit)

    approve_membership.short_description = "Approve selected memberships"

