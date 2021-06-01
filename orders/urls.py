from orders.models import Payment
from django.urls import path
from . import views

urlpatterns = [
    path('place_order/' , views.place_order, name = 'place_order'),

    path('pay_payments/', views.pay_payments, name = 'pay_payments'),
    
    path('success/', views.success, name = 'success'),
    path('razor_success/<int:pk>', views.razor_success, name = 'razor_success'),
    path('payments/<int:pk>/', views.payments, name = 'payments'),
    path('razorpay_payment/<int:pk>/', views.razorpay_payment, name = 'razorpay_payment'),
    path('confirm_order/<int:pk>',views.confirm_order, name = 'confirm_order'),
    path('cancel_order/<int:pk>',views.cancel_order, name = 'cancel_order'),
    path('orders_details/',views.orders_details, name = 'orders_details'),
    path('cancel_order_user/<int:pk>',views.cancel_order_user, name = 'cancel_order_user'),
]