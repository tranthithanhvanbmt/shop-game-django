from django.urls import path
from . import views

urlpatterns = [
    path('', views.wheel_list_view, name='wheel_list'),
    path('wheel/<int:wheel_id>/', views.wheel_detail_view, name='wheel_detail'),
    path('api/spin/<int:wheel_id>/', views.spin_api, name='spin_api'),
]