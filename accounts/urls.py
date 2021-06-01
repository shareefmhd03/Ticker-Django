
from django.urls import path,include
from . import views  



urlpatterns = [
   
    path('login/',views.user_login, name = 'user_login'),
    path('register/',views.user_register, name = 'user_register'),
    path('logout/', views.logout_view, name = 'user_logout'),
    path('forgot_password/', views.forgot_password, name = 'forgot_password'),
    path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate, name = 'resetpassword_validate'),
    path('reset_password/', views.reset_password, name = 'reset_password'),

    path('user_profile/<int:id>', views.user_profile, name = 'user_profile'),
    path('edit_profile/<int:id>', views.edit_profile, name = 'edit_profile'),
    path('profile_image/', views.profile_image, name = 'profile_image'),
    path('add_address', views.add_address, name = 'add_address'),
    path('add_address_in_checkout', views.add_address_in_checkout, name = 'add_address_in_checkout'),
    path('delete_address/<int:id>', views.delete_address, name = 'delete_address'),
    path('edit_address/<int:id>', views.edit_address, name = 'edit_address'),
    path('edit_address_in_checkout/<int:id>', views.edit_address_in_checkout, name = 'edit_address_in_checkout'),

    path('admin_login/',views.admin_login, name = 'admin_login'),
    path('admin_home/',views.admin_home, name = 'admin_home'),

    path('admin_logout/',views.admin_logout, name = 'admin_logout'),
  
    path('validate_email/', views.validate_email, name='validate_email'),
    path('validate_referralcode/', views.validate_referralcode, name='validate_referralcode'),

    path('otp_login/',views.otp_login, name= 'otp_login'),
    path('verify_otp/',views.verify_otp, name= 'verify_otp'),
    path('referrals',views.referrals, name= 'referrals'),
#  path('user_profile_coupons',views.user_profile_coupons, name= 'user_profile_coupons'),
]
