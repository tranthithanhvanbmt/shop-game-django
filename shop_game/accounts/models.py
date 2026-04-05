from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Người dùng mở rộng với số dư, tổng nạp và IP đăng ký."""
    balance = models.DecimalField("Số dư", max_digits=12, decimal_places=2, default=0)
    total_topup = models.DecimalField("Tổng nạp", max_digits=12, decimal_places=2, default=0)
    signup_ip = models.GenericIPAddressField("IP đăng ký", null=True, blank=True)

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"

    def __str__(self):
        return self.username


class LoginHistory(models.Model):
    """Lưu lịch sử đăng nhập và cảnh báo liên quan."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='login_histories')
    ip_address = models.GenericIPAddressField("IP đăng nhập", null=True, blank=True)
    login_time = models.DateTimeField("Thời gian đăng nhập", auto_now_add=True)
    is_success = models.BooleanField("Đăng nhập thành công", default=False)
    warning = models.TextField("Cảnh báo", null=True, blank=True)

    class Meta:
        verbose_name = "Lịch sử đăng nhập"
        verbose_name_plural = "Lịch sử đăng nhập"
        ordering = ['-login_time']

    def __str__(self):
        status = 'OK' if self.is_success else 'FAIL'
        return f"[{self.login_time}] {self.user.username} ({status})"
