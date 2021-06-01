from django.db import models
from accounts.models import Account
from store.models import Product

# Create your models here.


class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE) 
    payment_id = models.CharField(max_length=200, blank = True)
    payment_method =models.CharField(max_length=150)
    amount_paid =models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, default = 'paid')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_method

class Order(models.Model):
    STATUS = (
        ('Order placed', 'Order placed'),
        ('completed', 'completed'),
        ('cancelled','cancelled')
    )

    user= models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null= True)
    order_no = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    order_total= models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS, default = 'Order placed')
    shipping_status = models.CharField(max_length=20, blank=True, null=True, default='Order Placed')
    ip = models.CharField(max_length=20,blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now= True)


    def __str__(self):
        return self.first_name


class OrederProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete= models.SET_NULL, blank=True, null=True)
    user  = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity  = models.IntegerField()
    product_price = models.FloatField()
    ordered  =models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at =  models.DateTimeField(auto_now= True)

    def __str__(self):
        return self.product.product_name