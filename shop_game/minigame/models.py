from django.db import models
from django.conf import settings

# 1. BẢNG VÒNG QUAY (Tạo các vòng quay khác nhau: Vòng quay Kim Cương, Vòng quay Quân Huy...)
class Wheel(models.Model):
    name = models.CharField("Tên vòng quay", max_length=100)
    price = models.DecimalField("Giá mỗi lượt quay", max_digits=10, decimal_places=0, default=10000)
    image = models.ImageField("Ảnh vòng quay", upload_to='wheels/', null=True, blank=True)
    is_active = models.BooleanField("Đang hoạt động", default=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Vòng quay"
        verbose_name_plural = "Danh sách Vòng quay"

    def __str__(self):
        return f"{self.name} - {self.price}đ/lượt"

# 2. BẢNG PHẦN THƯỞNG (Các ô trên vòng quay)
class Reward(models.Model):
    wheel = models.ForeignKey(Wheel, on_delete=models.CASCADE, related_name='rewards', verbose_name="Thuộc vòng quay")
    name = models.CharField("Tên phần thưởng", max_length=100, help_text="VD: Trúng 100K, Trúng Nick VIP, Chúc may mắn lần sau")
    image = models.ImageField("Ảnh phần thưởng", upload_to='rewards/', null=True, blank=True)
    probability = models.FloatField("Tỷ lệ trúng (%)", default=10.0, help_text="Tổng các phần thưởng trong 1 vòng quay nên là 100%")
    value = models.DecimalField("Giá trị (Nếu trúng tiền)", max_digits=10, decimal_places=0, default=0, help_text="Số tiền cộng vào tài khoản nếu trúng")

    class Meta:
        verbose_name = "Phần thưởng"
        verbose_name_plural = "Các Phần thưởng"

    def __str__(self):
        return f"{self.name} ({self.probability}%)"

# 3. BẢNG LỊCH SỬ QUAY CỦA KHÁCH
class SpinHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Người chơi")
    wheel = models.ForeignKey(Wheel, on_delete=models.CASCADE, verbose_name="Vòng quay")
    prize_name = models.CharField("Tên phần thưởng", max_length=100, default='')
    created_at = models.DateTimeField("Thời gian quay", auto_now_add=True)

    class Meta:
        verbose_name = "Lịch sử quay"
        verbose_name_plural = "Lịch sử quay"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} quay {self.wheel.name} trúng {self.prize_name}"
