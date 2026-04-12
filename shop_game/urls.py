"""URL configuration for shop_game project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.contrib.staticfiles.views import serve as staticfiles_serve
from shop_game.shop.views import (
    home_view,
    category_detail_view,
    account_detail_view,
    buy_account_view,
    seller_create_account_view,
    seller_validate_image_url_view,
)

urlpatterns = [
    path('quan-ly-bi-mat/', admin.site.urls),
    path('', home_view, name='home'),

    path('category/<int:category_id>/', category_detail_view, name='category_detail'),
    path('account/<int:account_id>/', account_detail_view, name='account_detail'),
    path('buy/<int:account_id>/', buy_account_view, name='buy_account'),
    path('seller/create-account/', seller_create_account_view, name='seller_create_account'),
    path('seller/validate-image-url/', seller_validate_image_url_view, name='seller_validate_image_url'),
    
    # Khai báo đường dẫn tới app accounts
    path('auth/', include('shop_game.accounts.urls')),
    path('billing/', include('shop_game.billing.urls')),
    path('minigame/', include('shop_game.minigame.urls')),
    
    # URL xử lý chuyển đổi ngôn ngữ
    path('i18n/', include('django.conf.urls.i18n')), 
]

# Local dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Production: map /static/* và /media/* về file system để tránh lỗi asset trên hosting
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', staticfiles_serve),
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
