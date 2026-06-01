from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class GcondIDUserAdmin(UserAdmin):
    list_display = ("email", "first_name", "access_level", "is_approved", "is_blocked", "is_staff")
    list_filter = ("access_level", "is_approved", "is_blocked", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    filter_horizontal = ("authorized_condominiums",)
    fieldsets = UserAdmin.fieldsets + (
        ("GcondID", {"fields": ("access_level", "authorized_condominiums", "is_approved", "is_blocked")}),
    )

# Register your models here.

