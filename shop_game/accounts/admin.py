from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, LoginHistory


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin Shop', {'fields': ('balance', 'total_topup', 'signup_ip')}),
    )
    list_display = ['username', 'email', 'balance', 'total_topup', 'is_staff']
    search_fields = ['username', 'email']


class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'ip_address', 'is_success', 'warning']
    list_filter = ['is_success', 'login_time']
    search_fields = ['user__username', 'ip_address']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(LoginHistory, LoginHistoryAdmin)
