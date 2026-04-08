from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from shop_game.shop.models import GameCategory, AccountInventory, NickOrder
from shop_game.billing.models import CardTransaction, DepositTransaction


def index(request):
    categories = GameCategory.objects.filter(is_active=True).order_by('name')
    featured_categories = categories[:8]
    return render(request, 'core/index.html', {
        'categories': featured_categories,
        'all_categories': categories,
    })


def category_detail(request, slug):
    category = get_object_or_404(GameCategory, slug=slug, is_active=True)
    items = AccountInventory.objects.filter(category=category, status='AVAILABLE')
    return render(request, 'core/category_detail.html', {
        'category': category,
        'items': items,
    })


@login_required
def profile(request):
    orders = NickOrder.objects.filter(buyer=request.user).order_by('-created_at')
    deposits = sorted(
        list(DepositTransaction.objects.filter(user=request.user))
        + list(CardTransaction.objects.filter(user=request.user)),
        key=lambda item: item.created_at,
        reverse=True,
    )
    return render(request, 'core/profile.html', {
        'orders': orders,
        'deposits': deposits,
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('core:index')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Đăng ký thành công!')
            return redirect('core:index')
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại.')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
