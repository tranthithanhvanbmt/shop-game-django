from django import forms
from django.core.exceptions import ValidationError
from .models import SiteSetting, Banner, News
from .image_url_utils import download_image_from_url
import logging

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_MIME_TYPES = {
    'image/jpeg',
    'image/jpg',
    'image/pjpeg',
    'image/png',
    'image/x-png',
    'image/gif',
    'image/webp',
}


class SiteSettingForm(forms.ModelForm):
    """Form cho SiteSetting với xử lý lỗi image upload"""
    logo_url = forms.URLField(required=False, label="Link logo")
    favicon_url = forms.URLField(required=False, label="Link favicon")
    bank_qr_image_url = forms.URLField(required=False, label="Link ảnh QR nạp ngân hàng")

    class Meta:
        model = SiteSetting
        fields = ['site_name', 'logo', 'favicon', 'bank_qr_image', 'currency', 'hotline', 'facebook_link', 'maintenance_mode']

    def _get_url_value(self, field_name):
        return (self.cleaned_data.get(field_name) or self.data.get(field_name) or '').strip()

    def clean_logo(self):
        image = self.cleaned_data.get('logo')
        logo_url = self._get_url_value('logo_url')
        if not image and logo_url:
            image = download_image_from_url(
                image_url=logo_url,
                field_label='Logo',
                max_size_bytes=5 * 1024 * 1024,
                allowed_mime_types=ALLOWED_IMAGE_MIME_TYPES | {'image/x-icon', 'image/vnd.microsoft.icon'},
            )
            self.cleaned_data['logo'] = image
        return self._validate_image_field(image, 'Logo')

    def clean_favicon(self):
        image = self.cleaned_data.get('favicon')
        favicon_url = self._get_url_value('favicon_url')
        if not image and favicon_url:
            image = download_image_from_url(
                image_url=favicon_url,
                field_label='Favicon',
                max_size_bytes=5 * 1024 * 1024,
                allowed_mime_types=ALLOWED_IMAGE_MIME_TYPES | {'image/x-icon', 'image/vnd.microsoft.icon'},
            )
            self.cleaned_data['favicon'] = image
        return self._validate_image_field(image, 'Favicon')

    def clean_bank_qr_image(self):
        image = self.cleaned_data.get('bank_qr_image')
        bank_qr_url = self._get_url_value('bank_qr_image_url')
        if not image and bank_qr_url:
            image = download_image_from_url(
                image_url=bank_qr_url,
                field_label='Ảnh QR nạp ngân hàng',
                max_size_bytes=5 * 1024 * 1024,
                allowed_mime_types=ALLOWED_IMAGE_MIME_TYPES,
            )
            self.cleaned_data['bank_qr_image'] = image
        return self._validate_image_field(image, 'Ảnh QR nạp ngân hàng')

    def _validate_image_field(self, image, field_name):
        """Validate ảnh"""
        if image:
            # Kiểm tra kích thước file (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError(f"{field_name}: Kích thước ảnh không được vượt quá 5MB")
            
            # Kiểm tra định dạng file
            content_type = getattr(image, 'content_type', None)
            if content_type and content_type not in (ALLOWED_IMAGE_MIME_TYPES | {'image/x-icon', 'image/vnd.microsoft.icon'}):
                raise ValidationError(
                    f"{field_name}: Định dạng ảnh không được hỗ trợ. "
                    f"Chấp nhận: JPEG, PNG, GIF, WebP, ICO"
                )
            
            logger.info(f"✓ Validate {field_name}: {image.name} ({image.size} bytes)")
        return image


class BannerForm(forms.ModelForm):
    """Form cho Banner với xử lý lỗi image upload"""
    image_url = forms.URLField(required=False, label="Link ảnh Banner")

    class Meta:
        model = Banner
        fields = ['title', 'image', 'link', 'is_active', 'order']

    def _get_url_value(self, field_name):
        return (self.cleaned_data.get(field_name) or self.data.get(field_name) or '').strip()

    def clean_image(self):
        image = self.cleaned_data.get('image')
        image_url = self._get_url_value('image_url')
        if not image and image_url:
            image = download_image_from_url(
                image_url=image_url,
                field_label='Ảnh Banner',
                max_size_bytes=10 * 1024 * 1024,
                allowed_mime_types=ALLOWED_IMAGE_MIME_TYPES,
            )
            self.cleaned_data['image'] = image
        if image:
            # Kiểm tra kích thước file (max 10MB để cho Banner ảnh lớn)
            if image.size > 10 * 1024 * 1024:
                raise ValidationError("Kích thước ảnh Banner không được vượt quá 10MB")
            
            # Kiểm tra định dạng file
            content_type = getattr(image, 'content_type', None)
            if content_type and content_type not in ALLOWED_IMAGE_MIME_TYPES:
                raise ValidationError(f"Định dạng ảnh không được hỗ trợ. Chấp nhận: JPEG, PNG, GIF, WebP")
            
            logger.info(f"✓ Validate Banner ảnh: {image.name} ({image.size} bytes)")
        return image


class NewsForm(forms.ModelForm):
    """Form cho News với xử lý lỗi image upload"""
    image_url = forms.URLField(required=False, label="Link ảnh đại diện")

    class Meta:
        model = News
        fields = ['title', 'slug', 'image', 'content', 'is_published']

    def _get_url_value(self, field_name):
        return (self.cleaned_data.get(field_name) or self.data.get(field_name) or '').strip()

    def clean_image(self):
        image = self.cleaned_data.get('image')
        image_url = self._get_url_value('image_url')
        if not image and image_url:
            image = download_image_from_url(
                image_url=image_url,
                field_label='Ảnh đại diện',
                max_size_bytes=5 * 1024 * 1024,
                allowed_mime_types=ALLOWED_IMAGE_MIME_TYPES,
            )
            self.cleaned_data['image'] = image
        if image:
            # Kiểm tra kích thước file (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Kích thước ảnh không được vượt quá 5MB")
            
            # Kiểm tra định dạng file
            content_type = getattr(image, 'content_type', None)
            if content_type and content_type not in ALLOWED_IMAGE_MIME_TYPES:
                raise ValidationError(f"Định dạng ảnh không được hỗ trợ. Chấp nhận: JPEG, PNG, GIF, WebP")
            
            logger.info(f"✓ Validate tin tức ảnh: {image.name} ({image.size} bytes)")
        return image
