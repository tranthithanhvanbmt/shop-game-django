from django.urls import path
from . import views

urlpatterns = [
    path('deposit/', views.deposit_view, name='deposit'),
    path('bank-qr/', views.bank_qr_topup_view, name='bank_qr_topup'),
]
