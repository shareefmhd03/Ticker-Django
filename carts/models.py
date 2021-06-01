from accounts.models import Account
from django.db import models
from store.models import Product
from accounts.models import Account

# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True )

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    cart    = models.ForeignKey(Cart, on_delete = models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)


    def sub_total(self):
        # print('in_sub_total')
        sub_total = 0
        if self.product.offer_price:
            if self.product.coupon_price:
                sub_total += (self.product.offer_price-self.product.coupon_price) * self.quantity
                # print(sub_total,'if')
            else:
                sub_total += self.product.offer_price * self.quantity
                # print(sub_total,'iffff')
        elif  self.product.coupon_price and not self.product.offer_price:              
                sub_total += self.product.coupon_price * self.quantity
                # print(sub_total,'if')
        else:
            sub_total +=(self.product.price * self.quantity)
            # print(sub_total)
        return sub_total




        # if self.product.offer_price:
        #     sub_total = self.product.offer_price * self.quantity
        # else:
        #     sub_total = self.product.price * self.quantity
        

    def __str__(self):
        return self.product.product_name