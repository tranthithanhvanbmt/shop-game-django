from django import forms
from django.core.exceptions import ValidationError
from .models import Wheel, Reward
from shop_game.core.image_url_utils import download_image_from_url
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


class WheelForm(forms.ModelForm):
    """Form cho Wheel với xử lý lỗi image upload"""
    image_url = forms.URLField(required=False, label="Link ảnh vòng quay")

    class Meta:
        model = Wheel
        fields = ['name', 'price', 'image', 'is_active']

    def _get_url_value(self, field_name):
        return (self.cleaned_data.get(field_name) or self.data.get(field_name) or '').strip()

    def clean_image(self):
        image = self.cleaned_data.get('image')
        image_url = self._get_url_value('image_url')
        if not image and image_url:
            image = download_image_from_url(
                image_url=image_url,
                field_label='Ảnh vòng quay',
                max_size_bytes=5 * 1024 * 1024,
                allowed_mime_types=ALLOWED_IMAGE_MIME_TYPES,
            )
            self.cleaned_data['image'] = image
        if image:
            # Kiểm tra kích thước file (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Kích thước ảnh vòng quay không được vượt quá 5MB")
            
            # Kiểm tra định dạng file
            content_type = getattr(image, 'content_type', None)
            if content_type and content_type not in ALLOWED_IMAGE_MIME_TYPES:
                raise ValidationError(f"Định dạng ảnh không được hỗ trợ. Chấp nhận: JPEG, PNG, GIF, WebP")
            
            logger.info(f"✓ Validate vòng quay ảnh: {image.name} ({image.size} bytes)")
        return image


class RewardForm(forms.ModelForm):
    """Form cho Reward với xử lý lỗi image upload"""
    image_url = forms.URLField(required=False, label="Link ảnh phần thưởng")

    class Meta:
        model = Reward
        fields = ['wheel', 'name', 'image', 'probability', 'value']

    def _get_url_value(self, field_name):
        return (self.cleaned_data.get(field_name) or self.data.get(field_name) or '').strip()

    def clean_image(self):
        image = self.cleaned_data.get('image')
        image_url = self._get_url_value('image_url')
        if not image and image_url:
            image = download_image_from_url(
                image_url=image_url,
                field_label='Ảnh phần thưởng',
                max_size_bytes=5 * 1024 * 1024,
                allowed_mime_types=ALLOWED_IMAGE_MIME_TYPES,
            )
            self.cleaned_data['image'] = image
        if image:
            # Kiểm tra kích thước file (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Kích thước ảnh phần thưởng không được vượt quá 5MB")
            
            # Kiểm tra định dạng file
            content_type = getattr(image, 'content_type', None)
            if content_type and content_type not in ALLOWED_IMAGE_MIME_TYPES:
                raise ValidationError(f"Định dạng ảnh không được hỗ trợ. Chấp nhận: JPEG, PNG, GIF, WebP")
            
            logger.info(f"✓ Validate phần thưởng ảnh: {image.name} ({image.size} bytes)")
        return image
