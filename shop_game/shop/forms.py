from django import forms
from django.core.exceptions import ValidationError
from .models import GameCategory, AccountInventory
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


class GameCategoryForm(forms.ModelForm):
    """Form cho GameCategory với xử lý lỗi image upload"""
    image_url = forms.URLField(required=False, label="Link ảnh đại diện")

    class Meta:
        model = GameCategory
        fields = ['name', 'slug', 'image', 'description', 'is_active']

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
            
            logger.info(f"✓ Validate ảnh: {image.name} ({image.size} bytes, {image.content_type})")
        return image


class AccountInventoryForm(forms.ModelForm):
    """Form cho AccountInventory với xử lý lỗi image upload"""
    image_thumb_url = forms.URLField(required=False, label="Link ảnh bìa")
    image_1_url = forms.URLField(required=False, label="Link ảnh chi tiết 1")
    image_2_url = forms.URLField(required=False, label="Link ảnh chi tiết 2")

    class Meta:
        model = AccountInventory
        fields = [
            'category', 'username', 'password', 'login_method',
            'price', 'rank', 'details',
            'image_thumb', 'image_1', 'image_2',
            'status', 'submitted_by', 'is_approved'
        ]

    def _get_url_value(self, field_name):
        return (self.cleaned_data.get(field_name) or self.data.get(field_name) or '').strip()

    def clean_image_thumb(self):
        image = self.cleaned_data.get('image_thumb')
        image_thumb_url = self._get_url_value('image_thumb_url')
        if not image and image_thumb_url:
            image = download_image_from_url(
                image_url=image_thumb_url,
                field_label='Ảnh bìa',
                max_size_bytes=5 * 1024 * 1024,
                allowed_mime_types=ALLOWED_IMAGE_MIME_TYPES,
            )
            self.cleaned_data['image_thumb'] = image
        return self._validate_image_field(image, 'Ảnh bìa')

    def clean_image_1(self):
        image = self.cleaned_data.get('image_1')
        image_1_url = self._get_url_value('image_1_url')
        if not image and image_1_url:
            image = download_image_from_url(
                image_url=image_1_url,
                field_label='Ảnh chi tiết 1',
                max_size_bytes=5 * 1024 * 1024,
                allowed_mime_types=ALLOWED_IMAGE_MIME_TYPES,
            )
            self.cleaned_data['image_1'] = image
        return self._validate_image_field(image, 'Ảnh chi tiết 1')

    def clean_image_2(self):
        image = self.cleaned_data.get('image_2')
        image_2_url = self._get_url_value('image_2_url')
        if not image and image_2_url:
            image = download_image_from_url(
                image_url=image_2_url,
                field_label='Ảnh chi tiết 2',
                max_size_bytes=5 * 1024 * 1024,
                allowed_mime_types=ALLOWED_IMAGE_MIME_TYPES,
            )
            self.cleaned_data['image_2'] = image
        return self._validate_image_field(image, 'Ảnh chi tiết 2')

    def _validate_image_field(self, image, field_name):
        """Validate ảnh chung"""
        if image:
            # Kiểm tra kích thước file (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError(f"{field_name}: Kích thước ảnh không được vượt quá 5MB")
            
            # Kiểm tra định dạng file
            content_type = getattr(image, 'content_type', None)
            if content_type and content_type not in ALLOWED_IMAGE_MIME_TYPES:
                raise ValidationError(
                    f"{field_name}: Định dạng ảnh không được hỗ trợ. "
                    f"Chấp nhận: JPEG, PNG, GIF, WebP"
                )
            
            logger.info(f"✓ Validate {field_name}: {image.name} ({image.size} bytes)")
        return image
