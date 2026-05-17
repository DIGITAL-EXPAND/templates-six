from django.contrib import admin
from .models import Organisation


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
