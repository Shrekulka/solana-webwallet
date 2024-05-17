from django.contrib import admin

from applications.core.admin import CommonAdmin

from . import models


@admin.register(models.Wallet)
class WalletAdmin(CommonAdmin):
    list_display = ['user', 'name', 'status', 'created']
    list_filter = ['status']
    search_fields = ['user', 'name', 'description']
    date_hierarchy = 'created'
    ordering = ['-created']
