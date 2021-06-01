from django.contrib import admin

# Register your models here.
from .models import Payment, Order, OrederProduct
from orders import models



class OrderProductInline(admin.TabularInline):
    model = OrederProduct
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display =['order_no', 'first_name', 'email', 'order_total', 'is_ordered']
    inlines = [OrderProductInline]

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrederProduct)
