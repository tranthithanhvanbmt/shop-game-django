from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from decimal import Decimal, InvalidOperation
from urllib.parse import quote
from .models import CardProvider, CardTransaction, BankTopupTransaction
from shop_game.core.models import SiteSetting

@login_required  # Bắt buộc phải đăng nhập mới nạp được
def deposit_view(request):
    if request.method == 'POST':
        provider_code = (request.POST.get('provider') or '').strip().upper()
        value = request.POST.get('value')
        serial = (request.POST.get('serial') or '').strip()
        code = (request.POST.get('code') or '').strip()

        # 1. Kiểm tra dữ liệu đầu vào
        if not all([provider_code, value, serial, code]):
            messages.error(request, "Vui lòng nhập đầy đủ thông tin thẻ!")
            return redirect('home')

        try:
            declared_value = Decimal(value)
            if declared_value <= 0:
                raise InvalidOperation
        except (InvalidOperation, TypeError, ValueError):
            messages.error(request, "Mệnh giá thẻ không hợp lệ!")
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
            declared_value=declared_value,
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
    static_qr_url = (getattr(settings, 'BANK_QR_STATIC_IMAGE_URL', '') or '').strip()
    site_setting = SiteSetting.objects.first()

    admin_qr_url = ''
    if site_setting and site_setting.bank_qr_image:
        admin_qr_url = request.build_absolute_uri(site_setting.bank_qr_image.url)

    # Nếu có link ảnh QR cố định thì ưu tiên dùng luôn.
    # Dùng cho trường hợp user muốn hiển thị 1 ảnh ngân hàng cố định từ CDN.
    if not admin_qr_url and not static_qr_url and not account_no:
        messages.error(request, "Admin chưa cấu hình số tài khoản ngân hàng hoặc link ảnh QR.")
        return redirect('home')

    transfer_content = f"NAP {request.user.username}"
    if admin_qr_url:
        qr_url = admin_qr_url
    elif static_qr_url:
        qr_url = static_qr_url
    else:
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
