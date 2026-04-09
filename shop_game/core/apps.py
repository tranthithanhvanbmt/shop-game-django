from django.apps import AppConfig
import logging
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
                logger.info(f"Created media directory: {media_root}")
        except PermissionError:
            logger.warning(f"No permission to create media directory: {media_root}")
        except Exception as e:
            logger.warning(f"Could not create media directory: {e}")
        
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
                    logger.info(f"Created media subdirectory: {subdir}")
                except PermissionError:
                    logger.debug(f"No permission to create media subdirectory: {subdir}")
                except Exception as e:
                    logger.debug(f"Could not create media subdirectory {subdir}: {e}")
