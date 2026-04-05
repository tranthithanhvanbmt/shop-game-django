from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from .models import CustomUser
from shop_game.shop.models import NickOrder
from shop_game.billing.models import DepositTransaction
from shop_game.minigame.models import SpinHistory

# 1. ĐĂNG KÝ TÀI KHOẢN
def register_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p1 = request.POST.get('password')
        p2 = request.POST.get('re_password')

        # Kiểm tra mật khẩu khớp nhau
        if p1 != p2:
            messages.error(request, "Mật khẩu nhập lại không khớp!")
            return redirect('register')

        # Kiểm tra tài khoản đã tồn tại chưa
        if CustomUser.objects.filter(username=u).exists():
            messages.error(request, "Tên đăng nhập đã có người sử dụng!")
            return redirect('register')

        # Lấy IP của người dùng đăng ký
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Tạo user mới (Hàm create_user tự động mã hóa mật khẩu)
        user = CustomUser.objects.create_user(username=u, password=p1, signup_ip=ip)
        
        # Đăng nhập luôn sau khi đăng ký thành công
        login(request, user)
        messages.success(request, f"Chào mừng {u} đã gia nhập hệ thống!")
        return redirect('home')

    return render(request, 'register.html')

# 2. ĐĂNG NHẬP
def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        # Kiểm tra tài khoản mật khẩu
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, "Đăng nhập thành công!")
            return redirect('home')
        else:
            messages.error(request, "Sai tên tài khoản hoặc mật khẩu!")

    return render(request, 'login.html')

# 3. ĐĂNG XUẤT
def logout_view(request):
    logout(request)
    messages.success(request, "Bạn đã đăng xuất an toàn!")
    return redirect('home')

@login_required
def profile_view(request):
    orders = NickOrder.objects.filter(buyer=request.user).order_by('-created_at')
    deposits = DepositTransaction.objects.filter(user=request.user).order_by('-created_at')
    spins = SpinHistory.objects.filter(user=request.user).order_by('-created_at')
    
    # 1. Xử lý Đổi mật khẩu
    if request.method == 'POST' and 'change_password' in request.POST:
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Đổi mật khẩu thành công!')
            return redirect('profile')
        else:
            messages.error(request, 'Lỗi đổi mật khẩu! Vui lòng kiểm tra lại.')
    else:
        password_form = PasswordChangeForm(request.user)

    # 2. Xử lý Cập nhật Thông tin cá nhân
    if request.method == 'POST' and 'update_info' in request.POST:
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        messages.success(request, 'Cập nhật thông tin thành công!')
        return redirect('profile')

    context = {
        'orders': orders,
        'deposits': deposits,
        'spins': spins,
        'password_form': password_form
    }
    return render(request, 'profile.html', context)
