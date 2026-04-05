from django.contrib import admin
from .models import GameCategory, AccountInventory, NickOrder

class GameCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)} # Tự động tạo slug từ tên game

class AccountInventoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'login_method', 'price', 'status', 'created_at']
    list_filter = ['status', 'category', 'login_method']
    search_fields = ['username', 'id']

    # Ẩn mật khẩu ở danh sách ngoài, nhưng bấm vào trong vẫn xem được
    readonly_fields = ['created_at']

class NickOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'account', 'price_paid', 'created_at']
    list_filter = ['created_at']
    search_fields = ['buyer__username', 'account__id']

    # Không cho admin sửa đơn hàng đã hoàn thành để đảm bảo tính minh bạch
    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(GameCategory, GameCategoryAdmin)
admin.site.register(AccountInventory, AccountInventoryAdmin)
admin.site.register(NickOrder, NickOrderAdmin)
