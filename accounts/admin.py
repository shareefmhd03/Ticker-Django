from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, Profile


# Register your models here.

class AccountAdmin(UserAdmin):
    list_display= ('email', 'first_name', 'last_name', 'last_login', 'date_joined', 'is_active')
    list_display_links =('first_name', 'last_name')
    readonly_fields =('last_login', 'date_joined', )
    ordering = ('is_active',)

    filter_horizontal=()
    list_filter =()
    fieldsets =()

admin.site.register(Account, AccountAdmin)
admin.site.register(Profile)
