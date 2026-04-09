from django import forms
from django.core.exceptions import ValidationError
from .models import Wheel, Reward
import logging

logger = logging.getLogger(__name__)


class WheelForm(forms.ModelForm):
    """Form cho Wheel với xử lý lỗi image upload"""
    class Meta:
        model = Wheel
        fields = ['name', 'price', 'image', 'is_active']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Kiểm tra kích thước file (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Kích thước ảnh vòng quay không được vượt quá 5MB")
            
            # Kiểm tra định dạng file
            allowed_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in allowed_formats:
                raise ValidationError(f"Định dạng ảnh không được hỗ trợ. Chấp nhận: JPEG, PNG, GIF, WebP")
            
            logger.info(f"✓ Validate vòng quay ảnh: {image.name} ({image.size} bytes)")
        return image


class RewardForm(forms.ModelForm):
    """Form cho Reward với xử lý lỗi image upload"""
    class Meta:
        model = Reward
        fields = ['wheel', 'name', 'image', 'probability', 'value']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Kiểm tra kích thước file (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Kích thước ảnh phần thưởng không được vượt quá 5MB")
            
            # Kiểm tra định dạng file
            allowed_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in allowed_formats:
                raise ValidationError(f"Định dạng ảnh không được hỗ trợ. Chấp nhận: JPEG, PNG, GIF, WebP")
            
            logger.info(f"✓ Validate phần thưởng ảnh: {image.name} ({image.size} bytes)")
        return image
