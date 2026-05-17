from django.contrib import admin
from .models import Site, Venue, Space, Department, Position


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'city', 'province', 'country', 'is_active']
    list_filter = ['is_active', 'country', 'province']
    search_fields = ['name', 'code', 'city']
    readonly_fields = ['id']


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['name', 'site', 'venue_type', 'capacity', 'is_active']
    list_filter = ['venue_type', 'is_active', 'site']
    search_fields = ['name', 'site__name']
    readonly_fields = ['id']
    autocomplete_fields = ['site']


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'venue', 'space_type', 'capacity', 'is_bookable']
    list_filter = ['space_type', 'is_bookable', 'venue']
    search_fields = ['name', 'venue__name']
    readonly_fields = ['id']
    autocomplete_fields = ['venue']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department_type', 'site', 'is_active']
    list_filter = ['department_type', 'is_active']
    search_fields = ['name', 'code']
    readonly_fields = ['id']
    autocomplete_fields = ['site']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'level', 'site', 'reports_to', 'is_active']
    list_filter = ['level', 'is_active', 'department']
    search_fields = ['title', 'department__name']
    readonly_fields = ['id']
    autocomplete_fields = ['department', 'site', 'reports_to']
