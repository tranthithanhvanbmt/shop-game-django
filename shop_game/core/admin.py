from django.contrib import admin
from .models import SiteSetting, Banner, News

class SiteSettingAdmin(admin.ModelAdmin):
    # Khóa nút "Thêm mới" nếu đã có 1 cấu hình rồi (chỉ cho phép sửa)
    def has_add_permission(self, request):
        if SiteSetting.objects.exists():
            return False
        return True

class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'image', 'is_active', 'order']
    list_editable = ['is_active', 'order'] # Cho phép bật/tắt banner nhanh

class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'created_at']
    prepopulated_fields = {'slug': ('title',)} # Tự tạo slug từ tiêu đề

admin.site.register(SiteSetting, SiteSettingAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(News, NewsAdmin)
