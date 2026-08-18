from django.contrib import admin

from .models import Appointment, CustomerProfile, Service, Stylist


@admin.register(Stylist)
class StylistAdmin(admin.ModelAdmin):
    list_display = ("name", "work_start", "work_end", "is_active")
    list_filter = ("is_active",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_minutes", "price", "is_active")
    list_filter = ("is_active",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("customer", "stylist", "service", "date", "start_time", "end_time", "status")
    list_filter = ("status", "stylist", "date")
    search_fields = ("customer__username", "stylist__name")


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number")
