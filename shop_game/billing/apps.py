from django.apps import AppConfig


class BillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop_game.billing'
    verbose_name = '3. THẺ CÀO & TOPUP'

    def ready(self):
        import billing.signals  # Kích hoạt signals khi app khởi động
