from django.db import models
from django.conf import settings

# 1. BẢNG NHÀ CUNG CẤP THẺ (Viettel, Vina, Garena, Zing...)
class CardProvider(models.Model):
    name = models.CharField("Tên nhà mạng/Loại thẻ", max_length=50)
    code = models.CharField("Mã (Code)", max_length=20, unique=True, help_text="VD: VIETTEL, GARENA, ZING")
    discount_rate = models.DecimalField("Chiết khấu nạp (%)", max_digits=5, decimal_places=2, default=20.00, help_text="VD: 20% (Thẻ 100k khách nhận 80k)")
    is_active = models.BooleanField("Đang hoạt động", default=True)

    class Meta:
        verbose_name = "Nhà cung cấp thẻ"
        verbose_name_plural = "Nhà cung cấp thẻ"

    def __str__(self):
        return self.name


# 2. BẢNG LỊCH SỬ NẠP THẺ (Khách nạp thẻ cào để lấy số dư trên web)
class DepositTransaction(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Chờ xử lý'),
        ('SUCCESS', 'Thành công'),
        ('FAILED', 'Thất bại/Thẻ sai'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='deposits', verbose_name="Người nạp")
    provider = models.ForeignKey(CardProvider, on_delete=models.SET_NULL, null=True, verbose_name="Loại thẻ")

    declared_value = models.DecimalField("Mệnh giá khai báo", max_digits=12, decimal_places=0)
    real_value = models.DecimalField("Thực nhận", max_digits=12, decimal_places=0, default=0, help_text="Số tiền thực cộng vào web sau chiết khấu")

    serial = models.CharField("Số Serial", max_length=100)
    card_code = models.CharField("Mã thẻ (Pin)", max_length=100)

    status = models.CharField("Trạng thái", max_length=20, choices=STATUS_CHOICES, default='PENDING')
    note = models.TextField("Ghi chú/Lý do lỗi", null=True, blank=True)

    created_at = models.DateTimeField("Thời gian nạp", auto_now_add=True)
    updated_at = models.DateTimeField("Thời gian xử lý", auto_now=True)

    class Meta:
        verbose_name = "Đơn nạp thẻ"
        verbose_name_plural = "Lịch sử Nạp thẻ"
        ordering = ['-created_at']

    def __str__(self):
        return f"Nạp {self.declared_value} - {self.provider.name} - {self.user.username}"


# 3. BẢNG KHO THẺ CÀO (Thẻ admin tải lên để bán cho khách)
class CardInventory(models.Model):
    STATUS_CHOICES = (
        ('AVAILABLE', 'Chưa bán'),
        ('SOLD', 'Đã bán'),
    )

    provider = models.ForeignKey(CardProvider, on_delete=models.CASCADE, related_name='inventory', verbose_name="Loại thẻ")
    value = models.DecimalField("Mệnh giá thẻ", max_digits=12, decimal_places=0)

    serial = models.CharField("Số Serial", max_length=100)
    card_code = models.CharField("Mã thẻ (Pin)", max_length=100)

    status = models.CharField("Trạng thái", max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    bought_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người mua", related_name='bought_cards')
    bought_at = models.DateTimeField("Thời gian bán", null=True, blank=True)

    created_at = models.DateTimeField("Ngày nhập kho", auto_now_add=True)

    class Meta:
        verbose_name = "Kho thẻ cào (Để bán)"
        verbose_name_plural = "Kho thẻ cào (Để bán)"
        ordering = ['-created_at']

    def __str__(self):
        return f"Thẻ {self.provider.name} {self.value}đ ({self.status})"
