from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class AdminUser(UserAdmin):
    list_display = ['username', 'id', 'telegram_username', 'is_active', 'is_bot']
    list_filter = ['is_active', 'is_bot']
    search_fields = ['username', 'first_name', 'last_name', 'telegram_username']
    date_hierarchy = 'date_joined'
    ordering = ['-date_joined']
    fieldsets = (
        (None, {
            'fields': ('username', 'password',),
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email',),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined',),
        }),
        ('Telegram data', {
            'fields': ('telegram_id', 'telegram_username', 'telegram_language', 'is_bot', 'raw_data',),
        }),
        ('Solana data', {
            'fields': ('last_solana_derivation_path',),
        }),
        ('Binance data', {
            'fields': ('last_bsc_derivation_path',),
        }),
    )
