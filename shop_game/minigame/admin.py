from django.contrib import admin
from .models import Wheel, Reward, SpinHistory

class RewardInline(admin.TabularInline):
    model = Reward
    extra = 8 # Hiển thị sẵn 8 ô nhập phần thưởng khi tạo vòng quay

class WheelAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_active']
    inlines = [RewardInline] # Cho phép tạo phần thưởng ngay trong trang tạo Vòng quay

class SpinHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'wheel', 'prize_name', 'created_at']
    list_filter = ['wheel', 'created_at']

admin.site.register(Wheel, WheelAdmin)
admin.site.register(SpinHistory, SpinHistoryAdmin)
