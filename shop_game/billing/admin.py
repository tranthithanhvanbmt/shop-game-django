from django.contrib import admin
from .models import CardProvider, DepositTransaction, CardInventory, CardTransaction, BankTopupTransaction

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


class CardTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'provider', 'declared_value', 'real_value', 'status', 'processed_at', 'created_at']
    list_filter = ['status', 'provider', 'created_at']
    search_fields = ['user__username', 'serial', 'card_code']
    list_editable = ['status']
    readonly_fields = ['processed_at', 'created_at']


class BankTopupTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'transfer_content', 'status', 'processed_at', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'transfer_content']
    list_editable = ['status']
    readonly_fields = ['processed_at', 'created_at']

admin.site.register(CardProvider, CardProviderAdmin)
admin.site.register(DepositTransaction, DepositTransactionAdmin)
admin.site.register(CardInventory, CardInventoryAdmin)
admin.site.register(CardTransaction, CardTransactionAdmin)
admin.site.register(BankTopupTransaction, BankTopupTransactionAdmin)
