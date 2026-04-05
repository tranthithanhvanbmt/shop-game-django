from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Wheel, SpinHistory
import random

# 1. TRANG DANH SÁCH VÒNG QUAY
def wheel_list_view(request):
    wheels = Wheel.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'wheel_list.html', {'wheels': wheels})

# 2. TRANG HIỂN THỊ VÒNG QUAY
def wheel_detail_view(request, wheel_id):
    try:
        wheel = Wheel.objects.get(id=wheel_id, is_active=True)
    except Wheel.DoesNotExist:
        wheels = Wheel.objects.filter(is_active=True).order_by('-created_at')
        return render(request, 'wheel_list.html', {
            'wheels': wheels,
            'error_message': 'Không tìm thấy vòng quay bạn yêu cầu. Vui lòng chọn vòng quay khác.'
        })
    return render(request, 'wheel.html', {'wheel': wheel})

# 3. API XỬ LÝ KHI KHÁCH BẤM NÚT "QUAY" (Dùng cho Javascript)
@login_required
def spin_api(request, wheel_id):
    if request.method == 'POST':
        wheel = get_object_or_404(Wheel, id=wheel_id)
        user = request.user

        # Kiểm tra tiền
        if user.balance < wheel.price:
            return JsonResponse({'status': 'error', 'msg': 'Bạn không đủ số dư để quay!'})

        # Trừ tiền khách
        user.balance -= wheel.price
        user.save()

        # ==========================================
        # LOGIC TỶ LỆ TRÚNG THƯỞNG (GIẢ LẬP)
        # ==========================================
        prizes = [
            {'name': 'Trúng 5,000đ', 'value': 5000, 'rate': 50},
            {'name': 'Trúng 10,000đ', 'value': 10000, 'rate': 30},
            {'name': 'Trúng 20,000đ', 'value': 20000, 'rate': 15},
            {'name': 'Nổ Hũ 100,000đ', 'value': 100000, 'rate': 5},
        ]

        rand_num = random.randint(1, 100)
        current_rate = 0
        won_prize = None

        for prize in prizes:
            current_rate += prize['rate']
            if rand_num <= current_rate:
                won_prize = prize
                break

        user.balance += won_prize['value']
        user.save()

        SpinHistory.objects.create(
            user=user,
            wheel=wheel,
            prize_name=won_prize['name']
        )

        return JsonResponse({
            'status': 'success',
            'msg': f"Chúc mừng! Bạn đã {won_prize['name']}",
            'new_balance': user.balance,
            'prize_name': won_prize['name']
        })

    return JsonResponse({'status': 'error', 'msg': 'Lỗi hệ thống!'})
