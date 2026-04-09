from django.db import models, transaction
from django.db.models import F
from django.conf import settings
from django.utils import timezone

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
        provider_name = self.provider.name if self.provider else 'Unknown'
        return f"Nạp {self.declared_value} - {provider_name} - {self.user.username}"


class CardTransaction(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Chờ xử lý'),
        ('SUCCESS', 'Thành công'),
        ('FAILED', 'Thất bại'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='card_transactions', verbose_name="Người nạp")
    provider = models.ForeignKey(CardProvider, on_delete=models.SET_NULL, null=True, verbose_name="Loại thẻ")
    declared_value = models.DecimalField("Mệnh giá", max_digits=12, decimal_places=0)
    serial = models.CharField("Số seri", max_length=100)
    card_code = models.CharField("Mã thẻ", max_length=100)
    real_value = models.DecimalField("Thực nhận", max_digits=12, decimal_places=0, default=0)
    status = models.CharField("Trạng thái", max_length=20, choices=STATUS_CHOICES, default='PENDING')
    note = models.TextField("Ghi chú", null=True, blank=True)
    processed_at = models.DateTimeField("Thời gian xử lý", null=True, blank=True)
    created_at = models.DateTimeField("Thời gian tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Giao dịch thẻ cào"
        verbose_name_plural = "Giao dịch thẻ cào"
        ordering = ['-created_at']

    def __str__(self):
        return f"Card #{self.id} - {self.user.username} - {self.declared_value}"

    def save(self, *args, **kwargs):
        old_status = None
        old_processed_at = None
        if self.pk:
            previous = CardTransaction.objects.filter(pk=self.pk).values('status', 'processed_at').first()
            if previous:
                old_status = previous['status']
                old_processed_at = previous['processed_at']

        if self.status in ('SUCCESS', 'FAILED') and not self.processed_at:
            self.processed_at = timezone.now()

        # Nếu admin duyệt SUCCESS nhưng chưa nhập thực nhận thì tự tính theo chiết khấu
        if self.status == 'SUCCESS' and (self.real_value is None or self.real_value <= 0):
            discount = self.provider.discount_rate if self.provider else 0
            self.real_value = self.declared_value * (1 - (discount / 100))

        super().save(*args, **kwargs)

        if self.status == 'SUCCESS' and old_status != 'SUCCESS' and old_processed_at is None:
            with transaction.atomic():
                user = type(self.user).objects.select_for_update().get(pk=self.user_id)
                user.balance = F('balance') + self.real_value
                user.total_topup = F('total_topup') + self.real_value
                user.save(update_fields=['balance', 'total_topup'])


class BankTopupTransaction(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Chờ xác nhận'),
        ('SUCCESS', 'Đã cộng tiền'),
        ('FAILED', 'Thất bại'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bank_topups', verbose_name="Người nạp")
    amount = models.DecimalField("Số tiền nạp", max_digits=12, decimal_places=0)
    transfer_content = models.CharField("Nội dung chuyển khoản", max_length=255)
    qr_url = models.URLField("Link ảnh QR", max_length=600)
    status = models.CharField("Trạng thái", max_length=20, choices=STATUS_CHOICES, default='PENDING')
    note = models.TextField("Ghi chú", null=True, blank=True)
    processed_at = models.DateTimeField("Thời gian xử lý", null=True, blank=True)
    created_at = models.DateTimeField("Thời gian tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Nạp ngân hàng"
        verbose_name_plural = "Nạp ngân hàng"
        ordering = ['-created_at']

    def __str__(self):
        return f"BankTopup #{self.id} - {self.user.username} - {self.amount}"

    def save(self, *args, **kwargs):
        old_status = None
        old_processed_at = None
        if self.pk:
            previous = BankTopupTransaction.objects.filter(pk=self.pk).values('status', 'processed_at').first()
            if previous:
                old_status = previous['status']
                old_processed_at = previous['processed_at']

        if self.status in ('SUCCESS', 'FAILED') and not self.processed_at:
            self.processed_at = timezone.now()

        super().save(*args, **kwargs)

        if self.status == 'SUCCESS' and old_status != 'SUCCESS' and old_processed_at is None:
            with transaction.atomic():
                user = type(self.user).objects.select_for_update().get(pk=self.user_id)
                user.balance = F('balance') + self.amount
                user.total_topup = F('total_topup') + self.amount
                user.save(update_fields=['balance', 'total_topup'])


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
