from django.apps import AppConfig
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop_game.core'
    verbose_name = '4. CẤU HÌNH & TIN TỨC'

    def ready(self):
        """Tạo các thư mục media cần thiết khi Django khởi động"""
        from django.conf import settings
        
        # Tạo MEDIA_ROOT nếu không tồn tại
        media_root = Path(settings.MEDIA_ROOT)
        try:
            if not media_root.exists():
                media_root.mkdir(parents=True, exist_ok=True)
                logger.info(f"✓ Tạo media directory: {media_root}")
        except PermissionError:
            logger.warning(f"⚠ Không có quyền tạo media directory: {media_root}")
        except Exception as e:
            logger.warning(f"⚠ Không thể tạo media directory: {e}")
        
        # Tạo các subdirectory cụ thể
        subdirs = [
            'accounts/details',
            'accounts/thumbs',
            'banners',
            'categories',
            'news',
            'rewards',
            'wheels',
            'settings',
        ]
        
        for subdir in subdirs:
            dir_path = media_root / subdir
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"✓ Tạo thư mục: {subdir}")
                except PermissionError:
                    logger.debug(f"⚠ Không có quyền tạo thư mục {subdir}")
                except Exception as e:
                    logger.debug(f"⚠ Không thể tạo thư mục {subdir}: {e}")
