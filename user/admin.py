from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from user.forms import UserCreationForm
from user.models import AuthUser


class UserAdmin(DjangoUserAdmin):
    add_form = UserCreationForm
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    list_filter = ('is_superuser',)
    search_fields = ('email', 'username')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'is_staff', 'groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser', 'groups')}
        ),
    )
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(AuthUser, UserAdmin)