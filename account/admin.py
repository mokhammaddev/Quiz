from django.contrib import admin
from .models import Account
# from .forms import AccountCreationForm, AccountChangeForm


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    # form = AccountChangeForm
    # add_form = AccountCreationForm
    list_display = ['id', 'username', 'first_name',
                    'last_name', 'is_staff', 'is_superuser',
                    'is_active', 'date_created']
    readonly_fields = ['date_created', 'date_modified']
    list_display_links = ['id', 'username', 'first_name']
    list_filter = ['date_created', 'is_staff', 'is_active', 'is_superuser']
    search_fields = ['username', 'first_name', 'last_name']
    date_hierarchy = 'date_created'

    fieldsets = (
        (None, {'fields': ('username', 'password', 'first_name', 'last_name', 'image', 'bio')}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('date_modified', 'date_created')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'password1', 'password2'), }),
    )

