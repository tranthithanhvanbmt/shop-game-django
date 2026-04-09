from django.contrib import admin
import logging
from .models import Wheel, Reward, SpinHistory
from .forms import WheelForm, RewardForm

logger = logging.getLogger(__name__)


class RewardInline(admin.TabularInline):
    form = RewardForm
    model = Reward
    extra = 8  # Hiển thị sẵn 8 ô nhập phần thưởng khi tạo vòng quay


class WheelAdmin(admin.ModelAdmin):
    form = WheelForm
    list_display = ['name', 'price', 'is_active']
    inlines = [RewardInline]  # Cho phép tạo phần thưởng ngay trong trang tạo Vòng quay

    def save_model(self, request, obj, form, change):
        """Override để log khi save"""
        try:
            super().save_model(request, obj, form, change)
            logger.info(f"✓ Lưu Wheel: {obj.name}")
        except Exception as e:
            logger.error(f"✗ Lỗi khi lưu Wheel: {str(e)}", exc_info=True)
            raise


class SpinHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'wheel', 'prize_name', 'created_at']
    list_filter = ['wheel', 'created_at']


admin.site.register(Wheel, WheelAdmin)
admin.site.register(SpinHistory, SpinHistoryAdmin)
