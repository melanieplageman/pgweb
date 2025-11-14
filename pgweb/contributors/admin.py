from django import forms
from django.contrib import admin

from .models import Contributor, ContributorType, ContributorBadge


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
    search_fields = ('firstname', 'lastname', 'user__username',)


class ContributorBadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'org',)
    list_filter = ('org',)
    search_fields = ('name', 'org__name',)
    autocomplete_fields = ['org', ]


admin.site.register(ContributorType)
admin.site.register(Contributor, ContributorAdmin)
admin.site.register(ContributorBadge, ContributorBadgeAdmin)
