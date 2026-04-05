from django.db import models
from django.conf import settings

# 1. BẢNG DANH MỤC GAME (Ví dụ: Free Fire, Liên Quân, PUBG...)
class GameCategory(models.Model):
    name = models.CharField("Tên Game/Danh mục", max_length=100)
    slug = models.SlugField("Đường dẫn (Slug)", max_length=100, unique=True, help_text="Ví dụ: lien-quan-mobile")
    image = models.ImageField("Ảnh đại diện", upload_to='categories/', null=True, blank=True)
    description = models.TextField("Mô tả", null=True, blank=True)
    is_active = models.BooleanField("Hiển thị", default=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Danh mục Game"
        verbose_name_plural = "Danh mục Game"

    def __str__(self):
        return self.name


# 2. BẢNG KHO NICK (Chi tiết từng tài khoản game đang bán)
class AccountInventory(models.Model):
    STATUS_CHOICES = (
        ('AVAILABLE', 'Đang bán (Chưa ai mua)'),
        ('SOLD', 'Đã bán'),
        ('HIDDEN', 'Tạm ẩn'),
    )

    category = models.ForeignKey(GameCategory, on_delete=models.CASCADE, related_name='accounts', verbose_name="Thuộc Game")

    # Thông tin đăng nhập (Giao cho khách sau khi mua)
    username = models.CharField("Tài khoản đăng nhập", max_length=100)
    password = models.CharField("Mật khẩu", max_length=100)
    login_method = models.CharField("Kiểu đăng nhập", max_length=50, help_text="VD: Facebook, Garena, Google...", default="Garena")

    # Thông tin hiển thị cho khách xem trước khi mua
    price = models.DecimalField("Giá bán", max_digits=12, decimal_places=0, default=0)
    rank = models.CharField("Mức Rank", max_length=50, null=True, blank=True)
    details = models.TextField("Thông tin nổi bật", help_text="VD: Có nhiều skin súng VIP, đồ hiếm...", null=True, blank=True)

    # Hình ảnh minh họa cho nick
    image_thumb = models.ImageField("Ảnh bìa nick", upload_to='accounts/thumbs/', null=True, blank=True)
    image_1 = models.ImageField("Ảnh chi tiết 1", upload_to='accounts/details/', null=True, blank=True)
    image_2 = models.ImageField("Ảnh chi tiết 2", upload_to='accounts/details/', null=True, blank=True)

    status = models.CharField("Trạng thái", max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    created_at = models.DateTimeField("Ngày đăng", auto_now_add=True)

    class Meta:
        verbose_name = "Kho Nick"
        verbose_name_plural = "Kho Nick"
        ordering = ['-created_at']

    def __str__(self):
        return f"Nick #{self.id} - {self.category.name} - {self.price}đ"


# 3. BẢNG ĐƠN HÀNG MUA NICK
class NickOrder(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='nick_orders', verbose_name="Người mua")
    account = models.OneToOneField(AccountInventory, on_delete=models.CASCADE, verbose_name="Nick đã mua")
    price_paid = models.DecimalField("Giá lúc mua", max_digits=12, decimal_places=0, help_text="Lưu lại giá lúc mua phòng khi admin đổi giá nick sau này")
    created_at = models.DateTimeField("Thời gian mua", auto_now_add=True)

    class Meta:
        verbose_name = "Đơn mua Nick"
        verbose_name_plural = "Đơn mua Nick"
        ordering = ['-created_at']

    def __str__(self):
        return f"Đơn #{self.id} - {self.buyer.username} mua Nick #{self.account.id}"
