from django.db import models

# 1. BẢNG CẤU HÌNH WEB (Chỉ nên có 1 bản ghi duy nhất)
class SiteSetting(models.Model):
    site_name = models.CharField("Tên Website", max_length=100, default="Shop Game Siêu Rẻ")
    logo = models.ImageField("Logo Website", upload_to='settings/', null=True, blank=True)
    favicon = models.ImageField("Favicon (Icon tab)", upload_to='settings/', null=True, blank=True)
    currency = models.CharField("Tiền tệ", max_length=10, default="VNĐ")
    hotline = models.CharField("Hotline hỗ trợ", max_length=20, null=True, blank=True)
    facebook_link = models.URLField("Link Facebook", null=True, blank=True)
    maintenance_mode = models.BooleanField("Chế độ bảo trì", default=False, help_text="Bật lên để đóng web bảo trì")

    class Meta:
        verbose_name = "Cấu hình Website"
        verbose_name_plural = "Cấu hình Website"

    def __str__(self):
        return self.site_name

# 2. BẢNG BANNER (Trình diễn ảnh / Slider ở trang chủ)
class Banner(models.Model):
    title = models.CharField("Tiêu đề", max_length=100, blank=True)
    image = models.ImageField("Ảnh Banner", upload_to='banners/')
    link = models.CharField("Đường dẫn khi click", max_length=255, blank=True, help_text="VD: /danh-muc/free-fire")
    is_active = models.BooleanField("Hiển thị", default=True)
    order = models.IntegerField("Thứ tự hiển thị", default=0)

    class Meta:
        verbose_name = "Banner / Trình diễn ảnh"
        verbose_name_plural = "Banner / Trình diễn ảnh"
        ordering = ['order']

    def __str__(self):
        return f"Banner: {self.title or 'Không tên'}"

# 3. BẢNG TIN TỨC (Các bài viết thông báo)
class News(models.Model):
    title = models.CharField("Tiêu đề bài viết", max_length=200)
    slug = models.SlugField("Đường dẫn SEO", unique=True)
    image = models.ImageField("Ảnh đại diện", upload_to='news/', null=True, blank=True)
    content = models.TextField("Nội dung bài viết")
    is_published = models.BooleanField("Xuất bản", default=True)
    created_at = models.DateTimeField("Ngày đăng", auto_now_add=True)

    class Meta:
        verbose_name = "Tin tức"
        verbose_name_plural = "Tin tức"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
