from django.contrib import admin
from django.utils.html import format_html
from .models import SiteSetting, Banner, News

class SiteSettingAdmin(admin.ModelAdmin):
    # Khóa nút "Thêm mới" nếu đã có 1 cấu hình rồi (chỉ cho phép sửa)
    def has_add_permission(self, request):
        if SiteSetting.objects.exists():
            return False
        return True

class BannerAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'image_preview', 'link', 'is_active', 'order']
    list_editable = ['is_active', 'order']  # Cho phép bật/tắt và đổi thứ tự nhanh
    list_filter = ['is_active']
    search_fields = ['title', 'link']
    ordering = ['order', '-id']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:56px;border-radius:6px;" />', obj.image.url)
        return '-'

    image_preview.short_description = 'Xem trước'

class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'created_at']
    prepopulated_fields = {'slug': ('title',)} # Tự tạo slug từ tiêu đề

admin.site.register(SiteSetting, SiteSettingAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(News, NewsAdmin)
