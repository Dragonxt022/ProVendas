from django.contrib import admin
from .models import LicenseKey

class LicenseKeyAdmin(admin.ModelAdmin):
    list_filter = ('status',)  # Remova qualquer referência ao campo 'user'
    list_display = ('key', 'expiration_date', 'status')


admin.site.register(LicenseKey, LicenseKeyAdmin)
