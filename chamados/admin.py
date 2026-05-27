from django.contrib import admin

from .models import Ticket, TicketNotification


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "sector", "priority", "status", "requester", "technician", "created_at", "completed_at")
    list_filter = ("sector", "priority", "status", "created_at")
    search_fields = (
        "description",
        "solution",
        "requester__first_name",
        "requester__last_name",
        "requester__email",
        "technician__first_name",
        "technician__last_name",
        "technician__email",
    )


@admin.register(TicketNotification)
class TicketNotificationAdmin(admin.ModelAdmin):
    list_display = ("ticket", "recipient", "channel", "status", "created_at")
    list_filter = ("channel", "status", "created_at")
    search_fields = ("ticket__description", "recipient__first_name", "recipient__last_name", "recipient__email", "response")

# Register your models here.
