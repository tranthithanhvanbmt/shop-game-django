from decimal import Decimal
from django.db import migrations


def create_default_admin(apps, schema_editor):
    User = apps.get_model('accounts', 'CustomUser')
    username = 'admin'
    email = 'admin@shopdh6.com'
    password = 'Admin@1234'
    max_balance = Decimal('9999999999.99')

    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        if user.is_superuser and user.is_staff:
            user.balance = max_balance
            user.total_topup = max_balance
            user.save(update_fields=['balance', 'total_topup'])
        return

    User._default_manager.create_superuser(
        username=username,
        email=email,
        password=password,
        balance=max_balance,
        total_topup=max_balance,
    )


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_admin, reverse_code=migrations.RunPython.noop),
    ]
