from .models import CustomUser
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'username',
                    'email', 'first_name', 
                    'last_name', 'is_active', 
                    'is_staff', 'is_superuser', 
                    'last_login', 'date_joined', 'password','token_invalidated')

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('token_invalidated',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('token_invalidated',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)