from django.contrib import admin
from .models import CardProvider, DepositTransaction, CardInventory

class CardProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'discount_rate', 'is_active']
    search_fields = ['name', 'code']

class DepositTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'provider', 'declared_value', 'real_value', 'status', 'created_at']
    list_filter = ['status', 'provider', 'created_at']
    search_fields = ['user__username', 'serial', 'card_code']
    # Giúp admin có thể sửa trạng thái từ PENDING sang SUCCESS nhanh chóng
    list_editable = ['status']

class CardInventoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'provider', 'value', 'serial', 'status', 'bought_by', 'created_at']
    list_filter = ['status', 'provider', 'value']
    search_fields = ['serial', 'card_code', 'bought_by__username']

    # Ẩn mã thẻ khi chưa bán để bảo mật, admin chỉ nên thấy khi cần thiết
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'AVAILABLE':
            return [] # Hoặc ['card_code'] nếu bạn muốn admin cũng không được sửa mã thẻ
        return []

admin.site.register(CardProvider, CardProviderAdmin)
admin.site.register(DepositTransaction, DepositTransactionAdmin)
admin.site.register(CardInventory, CardInventoryAdmin)
