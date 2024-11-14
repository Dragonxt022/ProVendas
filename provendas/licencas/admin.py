from django.contrib import admin
from .models import LicenseKey

class LicenseKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'expiration_date', 'created_at', 'is_valid')
    search_fields = ('user__username', 'key')

admin.site.register(LicenseKey, LicenseKeyAdmin)
