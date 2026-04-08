from django.contrib import admin
from .models import GameCategory, AccountInventory, NickOrder

class GameCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)} # Tự động tạo slug từ tên game

class AccountInventoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'submitted_by', 'is_approved', 'login_method', 'price', 'status', 'created_at']
    list_filter = ['status', 'is_approved', 'category', 'login_method']
    search_fields = ['username', 'id']
    list_editable = ['is_approved', 'status']

    # Ẩn mật khẩu ở danh sách ngoài, nhưng bấm vào trong vẫn xem được
    readonly_fields = ['created_at']

class NickOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'account', 'price_paid', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['buyer__username', 'account__id']
    list_editable = ['status']

    @admin.action(description='Duyệt đơn: Hoàn thành')
    def mark_completed(self, request, queryset):
        queryset.update(status='COMPLETED')

    @admin.action(description='Hủy đơn và hoàn tiền')
    def cancel_and_refund(self, request, queryset):
        for order in queryset.select_related('buyer', 'account'):
            if order.status != 'CANCELLED':
                order.status = 'CANCELLED'
                order.save()

    actions = ['mark_completed', 'cancel_and_refund']

admin.site.register(GameCategory, GameCategoryAdmin)
admin.site.register(AccountInventory, AccountInventoryAdmin)
admin.site.register(NickOrder, NickOrderAdmin)
