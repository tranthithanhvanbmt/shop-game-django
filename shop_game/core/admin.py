from django.contrib import admin
from django.utils.html import format_html
import logging
from .models import SiteSetting, Banner, News
from .forms import SiteSettingForm, BannerForm, NewsForm

logger = logging.getLogger(__name__)


class SiteSettingAdmin(admin.ModelAdmin):
    form = SiteSettingForm
    
    # Khóa nút "Thêm mới" nếu đã có 1 cấu hình rồi (chỉ cho phép sửa)
    def has_add_permission(self, request):
        if SiteSetting.objects.exists():
            return False
        return True

    def save_model(self, request, obj, form, change):
        """Override để log khi save"""
        try:
            super().save_model(request, obj, form, change)
            logger.info(f"✓ Lưu SiteSetting")
        except Exception as e:
            logger.error(f"✗ Lỗi khi lưu SiteSetting: {str(e)}", exc_info=True)
            raise


class BannerAdmin(admin.ModelAdmin):
    form = BannerForm
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

    def save_model(self, request, obj, form, change):
        """Override để log khi save"""
        try:
            super().save_model(request, obj, form, change)
            logger.info(f"✓ Lưu Banner #{obj.id}")
        except Exception as e:
            logger.error(f"✗ Lỗi khi lưu Banner: {str(e)}", exc_info=True)
            raise


class NewsAdmin(admin.ModelAdmin):
    form = NewsForm
    list_display = ['title', 'is_published', 'created_at']
    prepopulated_fields = {'slug': ('title',)}  # Tự tạo slug từ tiêu đề

    def save_model(self, request, obj, form, change):
        """Override để log khi save"""
        try:
            super().save_model(request, obj, form, change)
            logger.info(f"✓ Lưu News: {obj.title}")
        except Exception as e:
            logger.error(f"✗ Lỗi khi lưu News: {str(e)}", exc_info=True)
            raise


admin.site.register(SiteSetting, SiteSettingAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(News, NewsAdmin)
