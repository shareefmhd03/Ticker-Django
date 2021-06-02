from django.contrib import admin
from . models import CategoryOffer, Coupons, Product, ProductOffer, CouponCode, ReviewRating

# Register your models here.
admin.site.register(Product)   
admin.site.register(ProductOffer)   
admin.site.register(CategoryOffer)   
admin.site.register(CouponCode)   
admin.site.register(Coupons)   
admin.site.register(ReviewRating)   