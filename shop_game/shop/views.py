from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import Http404, JsonResponse
from django.core.exceptions import ValidationError
from .models import AccountInventory, NickOrder, GameCategory
from shop_game.minigame.models import Wheel
from shop_game.core.models import Banner
from shop_game.core.image_url_utils import download_image_from_url


ALLOWED_IMAGE_MIME_TYPES = {
    'image/jpeg',
    'image/jpg',
    'image/pjpeg',
    'image/png',
    'image/x-png',
    'image/gif',
    'image/webp',
}


def home_view(request):
    games = GameCategory.objects.filter(is_active=True).order_by('-created_at')
    wheels = Wheel.objects.filter(is_active=True).order_by('-created_at')
    banners = Banner.objects.filter(is_active=True).order_by('order', '-id')
    context = {
        'games': games,
        'wheels': wheels,
        'banners': banners,
    }
    return render(request, 'index.html', context)


# 1. TRANG HIỂN THỊ DANH SÁCH NICK CỦA 1 GAME
def category_detail_view(request, category_id):
    category = get_object_or_404(GameCategory, id=category_id, is_active=True)
    accounts = AccountInventory.objects.filter(category=category, status='AVAILABLE', is_approved=True)

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


def account_detail_view(request, account_id):
    account = get_object_or_404(AccountInventory.objects.select_related('category'), id=account_id)
    order = getattr(account, 'nickorder', None)

    can_view_credentials = False
    can_view_public = account.status == 'AVAILABLE' and account.is_approved
    buyer_can_view_detail = (
        request.user.is_authenticated
        and order is not None
        and order.buyer_id == request.user.id
        and order.status in ('PENDING', 'COMPLETED')
    )
    buyer_can_view_credentials = (
        request.user.is_authenticated
        and order is not None
        and order.buyer_id == request.user.id
        and order.status == 'COMPLETED'
    )

    if buyer_can_view_credentials:
        can_view_credentials = True

    if not can_view_public and not buyer_can_view_detail:
        raise Http404

    return render(request, 'account_detail.html', {
        'account': account,
        'order': order,
        'can_purchase': account.status == 'AVAILABLE' and account.is_approved,
        'can_view_credentials': can_view_credentials,
    })


# 2. XỬ LÝ KHI KHÁCH BẤM NÚT "MUA NGAY"
@login_required
def buy_account_view(request, account_id):
    if request.method == 'POST':
        with transaction.atomic():
            account = get_object_or_404(
                AccountInventory.objects.select_for_update(),
                id=account_id
            )
            user = get_user_model().objects.select_for_update().get(pk=request.user.pk)

            if account.status != 'AVAILABLE' or not account.is_approved:
                messages.error(request, "Tài khoản đã được người khác mua hoặc đang chờ duyệt.")
                return redirect('category_detail', category_id=account.category.id)

            if user.balance < account.price:
                messages.error(request, "Số dư của bạn không đủ! Vui lòng nạp thêm tiền.")
                return redirect('category_detail', category_id=account.category.id)

            user.balance -= account.price
            user.save(update_fields=['balance'])

            account.status = 'SOLD'
            account.save(update_fields=['status'])

            NickOrder.objects.create(
                buyer=user,
                account=account,
                price_paid=account.price,
                status='PENDING'
            )

        messages.success(request, "Mua thành công! Đơn hàng đang chờ admin duyệt.")
        return redirect('category_detail', category_id=account.category.id)

    return redirect('home')


@login_required
def seller_create_account_view(request):
    if not getattr(request.user, 'is_seller', False):
        messages.error(request, "Bạn chưa được cấp quyền Cộng tác viên/Seller.")
        return redirect('profile')

    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        username = request.POST.get('username')
        password = request.POST.get('password')
        login_method = request.POST.get('login_method') or 'Garena'
        price = request.POST.get('price')
        rank = request.POST.get('rank')
        details = request.POST.get('details')
        image_thumb_url = request.POST.get('image_thumb_url', '')
        image_1_url = request.POST.get('image_1_url', '')
        image_2_url = request.POST.get('image_2_url', '')

        category = get_object_or_404(GameCategory, id=category_id, is_active=True)

        image_thumb_file = request.FILES.get('image_thumb')
        image_1_file = request.FILES.get('image_1')
        image_2_file = request.FILES.get('image_2')

        try:
            if not image_thumb_file and image_thumb_url:
                image_thumb_file = download_image_from_url(
                    image_url=image_thumb_url,
                    field_label='Ảnh bìa',
                    max_size_bytes=5 * 1024 * 1024,
                    allowed_mime_types=ALLOWED_IMAGE_MIME_TYPES,
                )

            if not image_1_file and image_1_url:
                image_1_file = download_image_from_url(
                    image_url=image_1_url,
                    field_label='Ảnh chi tiết 1',
                    max_size_bytes=5 * 1024 * 1024,
                    allowed_mime_types=ALLOWED_IMAGE_MIME_TYPES,
                )

            if not image_2_file and image_2_url:
                image_2_file = download_image_from_url(
                    image_url=image_2_url,
                    field_label='Ảnh chi tiết 2',
                    max_size_bytes=5 * 1024 * 1024,
                    allowed_mime_types=ALLOWED_IMAGE_MIME_TYPES,
                )
        except ValidationError as exc:
            messages.error(request, str(exc))
            categories = GameCategory.objects.filter(is_active=True).order_by('name')
            return render(request, 'seller_create_account.html', {
                'categories': categories,
                'form_data': request.POST,
            })

        AccountInventory.objects.create(
            category=category,
            username=username,
            password=password,
            login_method=login_method,
            price=price,
            rank=rank,
            details=details,
            image_thumb=image_thumb_file,
            image_1=image_1_file,
            image_2=image_2_file,
            status='HIDDEN',
            submitted_by=request.user,
            is_approved=False,
        )
        messages.success(request, "Đăng bán thành công. Tài khoản đang ở trạng thái chờ duyệt.")
        return redirect('profile')

    categories = GameCategory.objects.filter(is_active=True).order_by('name')
    return render(request, 'seller_create_account.html', {'categories': categories})


@login_required
@require_POST
def seller_validate_image_url_view(request):
    if not getattr(request.user, 'is_seller', False):
        return JsonResponse({'ok': False, 'message': 'Bạn chưa được cấp quyền Cộng tác viên/Seller.'}, status=403)

    image_url = (request.POST.get('image_url') or '').strip()
    field_label = (request.POST.get('field_label') or 'Ảnh').strip()[:80]

    if not image_url:
        return JsonResponse({'ok': False, 'message': f'{field_label}: Vui lòng nhập link ảnh.'}, status=400)

    try:
        uploaded = download_image_from_url(
            image_url=image_url,
            field_label=field_label,
            max_size_bytes=5 * 1024 * 1024,
            allowed_mime_types=ALLOWED_IMAGE_MIME_TYPES,
        )
    except ValidationError as exc:
        return JsonResponse({'ok': False, 'message': str(exc)}, status=400)

    return JsonResponse({
        'ok': True,
        'message': f'{field_label}: Link hợp lệ ({uploaded.name}, {uploaded.size} bytes).',
    })
