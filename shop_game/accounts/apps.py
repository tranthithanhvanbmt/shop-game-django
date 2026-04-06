import os
from decimal import Decimal

from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop_game.accounts'
    verbose_name = '5. TÀI KHOẢN'

    def ready(self):
        self.create_default_admin()

    def create_default_admin(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@shopdh6.com')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'Admin@1234')
        max_balance = Decimal('9999999999.99')

        try:
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                if not user.is_superuser or not user.is_staff:
                    return
                user.balance = max_balance
                user.total_topup = max_balance
                user.save(update_fields=['balance', 'total_topup'])
            else:
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    balance=max_balance,
                    total_topup=max_balance,
                )
        except (OperationalError, ProgrammingError):
            # Database tables are not ready yet (migration phase)
            return
        except Exception:
            return
