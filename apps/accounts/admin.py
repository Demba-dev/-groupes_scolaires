from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Rôle', {'fields': ('role', 'telephone')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Rôle', {'fields': ('role', 'telephone')}),
    )
    list_display = ('username', 'get_full_name', 'role', 'is_staff', 'is_active', 'last_login')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')