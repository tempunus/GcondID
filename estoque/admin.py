from django.contrib import admin

from .models import StockItem, StockMovement


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ("condominium", "name", "sector", "category", "current_quantity", "minimum_quantity", "location")
    list_filter = ("condominium", "sector", "category")
    search_fields = ("name", "category", "location")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("item", "movement_type", "quantity", "user", "created_at")
    list_filter = ("movement_type", "created_at")
    search_fields = ("item__name", "notes")

# Register your models here.

