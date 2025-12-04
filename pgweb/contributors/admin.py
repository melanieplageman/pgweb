from django import forms
from django.contrib import admin

from .models import Contributor, ContributorType, ContributorBadge, ContributorBadgeAward, ContributorBadgeRequest


class ContributorAdminForm(forms.ModelForm):
    class Meta:
        model = Contributor
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(ContributorAdminForm, self).__init__(*args, **kwargs)


class ContributorAdmin(admin.ModelAdmin):
    form = ContributorAdminForm
    autocomplete_fields = ['user', ]
    list_display = ('__str__', 'user', 'ctype',)
    list_filter = ('ctype',)
    ordering = ('firstname', 'lastname',)
    search_fields = ('firstname', 'lastname', 'user__username', 'email',)


class ContributorBadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'org',)
    list_filter = ('org',)
    search_fields = ('name', 'org__name',)
    autocomplete_fields = ['org', ]


class ContributorBadgeAwardAdmin(admin.ModelAdmin):
    list_display = ('contributor', 'badge', 'awarded_date', 'active',)
    list_filter = ('active', 'badge', 'awarded_date',)
    search_fields = ('contributor__firstname', 'contributor__lastname', 'badge__name',)
    autocomplete_fields = ['contributor', 'badge', ]
    date_hierarchy = 'awarded_date'
    list_editable = ('active',)  # Allow editing active status directly from list view
    fields = ('contributor', 'badge', 'awarded_date', 'active')
    readonly_fields = ('awarded_date',)


class ContributorBadgeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'contributor', 'requested_date',)
    list_filter = ('badge', 'requested_date',)
    search_fields = ('user__username', 'user__email', 'badge__name', 'justification',)
    readonly_fields = ('requested_date', 'user', 'contributor', 'badge', 'justification', 'status')
    date_hierarchy = 'requested_date'

    def has_add_permission(self, request):
        # Users create requests through the web form, not admin
        return False


admin.site.register(ContributorType)
admin.site.register(Contributor, ContributorAdmin)
admin.site.register(ContributorBadge, ContributorBadgeAdmin)
admin.site.register(ContributorBadgeAward, ContributorBadgeAwardAdmin)
admin.site.register(ContributorBadgeRequest, ContributorBadgeRequestAdmin)
