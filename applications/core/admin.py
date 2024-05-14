from django.contrib import admin
from django.utils.html import mark_safe

from . import models


class CommonAdmin(admin.ModelAdmin):
    list_filter = ['status', 'created']
    readonly_fields = ['created', 'modified']
    actions = ['make_published', 'make_drafted']

    def make_published(self, request, queryset):
        queryset.update(status=models.Common.Status.PUBLISHED)

    make_published.short_description = 'Выставить статус "Опубликовано"'

    def make_drafted(self, request, queryset):
        queryset.update(status=models.Common.Status.DRAFT)

    make_drafted.short_description = 'Выставить статус "Черновик"'


class CommonInlineAdmin:
    readonly_fields = ['created', 'modified']
