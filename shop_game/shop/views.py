from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AccountInventory, NickOrder, GameCategory
from shop_game.minigame.models import Wheel


def home_view(request):
    games = GameCategory.objects.filter(is_active=True).order_by('-created_at')
    wheels = Wheel.objects.filter(is_active=True).order_by('-created_at')
    context = {
        'games': games,
        'wheels': wheels,
    }
    return render(request, 'index.html', context)


# 1. TRANG HIỂN THỊ DANH SÁCH NICK CỦA 1 GAME
def category_detail_view(request, category_id):
    category = get_object_or_404(GameCategory, id=category_id, is_active=True)
    accounts = AccountInventory.objects.filter(category=category, status='AVAILABLE')

    # --- LOGIC LỌC TÌM KIẾM ---
    search_id = request.GET.get('search_id')
    price_filter = request.GET.get('price')
    rank_filter = request.GET.get('rank')

    if search_id:
        accounts = accounts.filter(id=search_id)

    if price_filter:
        if price_filter == '1':
            accounts = accounts.filter(price__lt=50000)
        elif price_filter == '2':
            accounts = accounts.filter(price__gte=50000, price__lte=200000)
        elif price_filter == '3':
            accounts = accounts.filter(price__gt=200000)

    if rank_filter:
        accounts = accounts.filter(rank__icontains=rank_filter)

    accounts = accounts.order_by('-created_at')

    context = {
        'category': category,
        'accounts': accounts,
        'search_id': search_id,
        'price_filter': price_filter,
        'rank_filter': rank_filter,
    }
    return render(request, 'category_detail.html', context)


# 2. XỬ LÝ KHI KHÁCH BẤM NÚT "MUA NGAY"
@login_required
def buy_account_view(request, account_id):
    if request.method == 'POST':
        account = get_object_or_404(AccountInventory, id=account_id)
        user = request.user

        if account.status != 'AVAILABLE':
            messages.error(request, "Rất tiếc, tài khoản này đã có người nhanh tay mua mất!")
            return redirect('category_detail', category_id=account.category.id)

        if user.balance < account.price:
            messages.error(request, "Số dư của bạn không đủ! Vui lòng nạp thêm tiền.")
            return redirect('category_detail', category_id=account.category.id)

        user.balance -= account.price
        user.save()

        account.status = 'SOLD'
        account.save()

        NickOrder.objects.create(
            buyer=user,
            account=account,
            price_paid=account.price
        )

        messages.success(request, f"🎉 MUA THÀNH CÔNG! Tài khoản: {account.username} | Mật khẩu: {account.password}")
        return redirect('category_detail', category_id=account.category.id)

    return redirect('home')
