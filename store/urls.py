

from django.urls import path,include
from . import views

urlpatterns = [
    
    path('', views.store, name= 'store'),     
       
    path('order_mgmt/',views.order_management, name = 'order_management'),
    path('shipping_status/<int:id>',views.shipping_status, name = 'shipping_status'),
    path('order_tracking/<int:product_id>', views.order_tracking, name = 'order_tracking'),
    path('submit_review/<int:product_id>/', views.submit_review, name= 'submit_review'),

    path('view_orders/<int:id>',views.view_orders, name = 'view_orders'),
    path('edit_order/<int:id>',views.edit_order, name = 'edit_order'),
    path('search/',views.search, name = 'search'),
    path('weekly_report/',views.weekly_report, name = 'weekly_report'),
    path('monthly_report/',views.monthly_report, name = 'monthly_report'),
    path('yearly_report/',views.yearly_report, name = 'yearly_report'),
   
    path('offer_mgmt_prod/',views.offer_management_prod, name = 'offer_management_prod'),
    path('offer_mgmt_view_products/',views.offer_management_view_products, name = 'offer_management_view_products'),
    path('offer_mgmt_cat/',views.offer_management_cat, name = 'offer_management_cat'),
    path('add_product_offer/<int:product_id>/',views.add_product_offer, name= 'add_product_offer'),
    path('add_category_offer/',views.add_category_offer, name= 'add_category_offer'),
    
    path('del_product_offer/<int:product_id>/',views.del_product_offer, name='del_product_offer'),
   
    path('del_category_offer/<int:category_id>/',views.del_category_offer, name='del_category_offer'),
    
    

    path('product_mgmt/',views.product_management, name = 'product_management'),
    
    path('add_product/',views.add_product, name = 'add_product'),
    path('del_product/<int:pk>',views.del_product, name = 'del_product'),
    path('edit_product/<slug:slug>',views.edit_product, name = 'edit_product'),
    path('add_category/',views.add_category, name = 'add_category'),
    path('user_mgmt/',views.user_management, name = 'user_management'), 
    path('del_user/<int:pk>',views.del_user, name = 'del_user'),
    path('block_user/<int:pk>',views.block_user, name = 'block_user'),
    path('category_mgmt/',views.category_management, name = 'category_management'),
    path('del_category/<int:pk>',views.del_category, name = 'del_category'),
    path('edit_category/<int:pk>',views.edit_category, name = 'edit_category'),
    path('category/<slug:category_slug>/', views.store, name= 'products_by_category'),     
    path('<slug:category_slug>/<slug:product_slug>/', views.product_view, name= 'product_view'),  

    
]

