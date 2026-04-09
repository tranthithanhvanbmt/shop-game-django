from django import forms
from django.core.exceptions import ValidationError
from .models import SiteSetting, Banner, News
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
    class Meta:
        model = SiteSetting
        fields = ['site_name', 'logo', 'favicon', 'currency', 'hotline', 'facebook_link', 'maintenance_mode']

    def clean_logo(self):
        return self._validate_image_field(self.cleaned_data.get('logo'), 'Logo')

    def clean_favicon(self):
        return self._validate_image_field(self.cleaned_data.get('favicon'), 'Favicon')

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
    class Meta:
        model = Banner
        fields = ['title', 'image', 'link', 'is_active', 'order']

    def clean_image(self):
        image = self.cleaned_data.get('image')
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
    class Meta:
        model = News
        fields = ['title', 'slug', 'image', 'content', 'is_published']

    def clean_image(self):
        image = self.cleaned_data.get('image')
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
