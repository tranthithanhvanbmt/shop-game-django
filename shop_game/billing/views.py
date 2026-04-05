from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CardProvider, DepositTransaction

@login_required  # Bắt buộc phải đăng nhập mới nạp được
def deposit_view(request):
    if request.method == 'POST':
        provider_code = request.POST.get('provider')
        value = request.POST.get('value')
        serial = request.POST.get('serial')
        code = request.POST.get('code')

        # 1. Kiểm tra dữ liệu đầu vào
        if not all([provider_code, value, serial, code]):
            messages.error(request, "Vui lòng nhập đầy đủ thông tin thẻ!")
            return redirect('home')

        # 2. Tìm nhà mạng trong DB
        try:
            provider = CardProvider.objects.get(code=provider_code, is_active=True)
        except CardProvider.DoesNotExist:
            messages.error(request, "Loại thẻ này hiện không hỗ trợ!")
            return redirect('home')

        # 3. Tạo đơn nạp ở trạng thái PENDING (Chờ duyệt)
        DepositTransaction.objects.create(
            user=request.user,
            provider=provider,
            declared_value=value,
            serial=serial,
            card_code=code,
            status='PENDING'
        )

        messages.success(request, "Gửi thẻ thành công! Vui lòng đợi Admin kiểm tra.")
        return redirect('home')
    
    return redirect('home')
