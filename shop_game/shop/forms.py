from django import forms
from django.core.exceptions import ValidationError
from .models import GameCategory, AccountInventory
import logging

logger = logging.getLogger(__name__)


class GameCategoryForm(forms.ModelForm):
    """Form cho GameCategory với xử lý lỗi image upload"""
    class Meta:
        model = GameCategory
        fields = ['name', 'slug', 'image', 'description', 'is_active']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Kiểm tra kích thước file (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Kích thước ảnh không được vượt quá 5MB")
            
            # Kiểm tra định dạng file
            allowed_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in allowed_formats:
                raise ValidationError(f"Định dạng ảnh không được hỗ trợ. Chấp nhận: JPEG, PNG, GIF, WebP")
            
            logger.info(f"✓ Validate ảnh: {image.name} ({image.size} bytes, {image.content_type})")
        return image


class AccountInventoryForm(forms.ModelForm):
    """Form cho AccountInventory với xử lý lỗi image upload"""
    class Meta:
        model = AccountInventory
        fields = [
            'category', 'username', 'password', 'login_method',
            'price', 'rank', 'details',
            'image_thumb', 'image_1', 'image_2',
            'status', 'submitted_by', 'is_approved'
        ]

    def clean_image_thumb(self):
        return self._validate_image_field(self.cleaned_data.get('image_thumb'), 'Ảnh bìa')

    def clean_image_1(self):
        return self._validate_image_field(self.cleaned_data.get('image_1'), 'Ảnh chi tiết 1')

    def clean_image_2(self):
        return self._validate_image_field(self.cleaned_data.get('image_2'), 'Ảnh chi tiết 2')

    def _validate_image_field(self, image, field_name):
        """Validate ảnh chung"""
        if image:
            # Kiểm tra kích thước file (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError(f"{field_name}: Kích thước ảnh không được vượt quá 5MB")
            
            # Kiểm tra định dạng file
            allowed_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in allowed_formats:
                raise ValidationError(
                    f"{field_name}: Định dạng ảnh không được hỗ trợ. "
                    f"Chấp nhận: JPEG, PNG, GIF, WebP"
                )
            
            logger.info(f"✓ Validate {field_name}: {image.name} ({image.size} bytes)")
        return image
