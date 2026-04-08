from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from urllib.parse import quote
from .models import CardProvider, CardTransaction, BankTopupTransaction

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
        CardTransaction.objects.create(
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


@login_required
def bank_qr_topup_view(request):
    if request.method != 'POST':
        return redirect('home')

    amount = request.POST.get('amount')
    if not amount or not amount.isdigit() or int(amount) <= 0:
        messages.error(request, "Số tiền nạp không hợp lệ.")
        return redirect('home')

    bank_code = getattr(settings, 'BANK_QR_BANK_CODE', 'MB')
    account_no = getattr(settings, 'BANK_QR_ACCOUNT_NO', '')
    account_name = getattr(settings, 'BANK_QR_ACCOUNT_NAME', '')
    if not account_no:
        messages.error(request, "Admin chưa cấu hình số tài khoản ngân hàng để nạp QR.")
        return redirect('home')

    transfer_content = f"NAP {request.user.username}"
    encoded_content = quote(transfer_content)
    encoded_account_name = quote(account_name)
    qr_url = (
        f"https://img.vietqr.io/image/{bank_code}-{account_no}-compact2.png"
        f"?amount={amount}&addInfo={encoded_content}&accountName={encoded_account_name}"
    )

    tx = BankTopupTransaction.objects.create(
        user=request.user,
        amount=amount,
        transfer_content=transfer_content,
        qr_url=qr_url,
        status='PENDING',
    )

    return render(request, 'bank_qr.html', {'tx': tx})
