from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DepositTransaction

@receiver(post_save, sender=DepositTransaction)
def update_user_balance(sender, instance, created, **kwargs):
    # Chỉ xử lý khi đơn hàng được cập nhật thành SUCCESS
    if instance.status == 'SUCCESS' and instance.real_value == 0:
        user = instance.user
        
        # Tính toán số tiền thực nhận sau khi trừ chiết khấu của nhà mạng
        discount = instance.provider.discount_rate
        amount_to_add = instance.declared_value * (1 - (discount / 100))
        
        # Cập nhật số dư và tổng nạp cho User
        user.balance += amount_to_add
        user.total_topup += amount_to_add
        user.save()
        
        # Lưu lại số tiền thực nhận vào đơn nạp để làm bằng chứng
        instance.real_value = amount_to_add
        instance.save()
