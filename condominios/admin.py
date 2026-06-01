from django.contrib import admin

from .models import Condominium


@admin.register(Condominium)
class CondominiumAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "state", "is_active")
    list_filter = ("is_active", "state")
    search_fields = ("name", "cnpj", "city", "address")
