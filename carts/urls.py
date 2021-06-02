from django.urls import path
from . import views


urlpatterns =[
    path('', views.cart, name = 'cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name = 'add_to_cart'),
    path('remove_cart/<int:product_id>/', views.remove_cart, name = 'remove_cart'),
    path('delete_cart_item/<int:product_id>/', views.delete_cart_item, name = 'delete_cart_item'),
    path('coupon_verify/', views.coupon_verify, name = 'coupon_verify'),
    path('coupon_confirm/', views.coupon_verify, name = 'coupon_confirm'),
    path('checkout/', views.checkout, name = 'checkout'),
    path('validate_coupon/', views.validate_coupon, name= 'validate_coupon'),
    path('get_address/' ,views.get_address, name = 'get_address'),
    path('add_cart/<int:id>' ,views.add_cart, name = 'add_cart'),
    
    # path('rem_cart/<int:id>' ,views.rem_cart, name = 'rem_cart')
    
]
