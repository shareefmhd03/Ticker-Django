from django.db.models.aggregates import Avg, Count
from accounts.models import Account
from typing import FrozenSet
from django.db import models
from category.models import Category
from django.urls import reverse
from category.models import Category

# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=150, unique=True)
    slug  = models.SlugField(max_length=150, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price  = models.IntegerField()
    offer_price = models.IntegerField(blank=True, null=True)
    coupon_price = models.IntegerField(blank=True, null=True)
    image1 = models.ImageField(upload_to= 'photos/products')
    image2 = models.ImageField(upload_to= 'photos/products')
    image3 = models.ImageField(upload_to= 'photos/products')
    image4 = models.ImageField(upload_to= 'photos/products')
    stock  = models.IntegerField()
    is_available = models.BooleanField(default= True)
    category = models.ForeignKey(Category, on_delete= models.CASCADE)
    created_date  = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    brand= models.CharField(max_length=30)
    gender= models.CharField(max_length=30)
    strap_colour= models.CharField(max_length=30)
    water_resistance= models.CharField(max_length=30)
    analogue_or_digital= models.CharField(max_length=30)
    glass= models.CharField(max_length=30)
    strap_type= models.CharField(max_length=30)  
    model_name= models.CharField(max_length=30)


    def get_url(self):
        return reverse('product_view',args = [self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

    def average_review(self):
        review = ReviewRating.objects.filter(product= self, status = True).aggregate(average = Avg('rating'))
        avg = 0
        if review['average'] is not None:
            avg = float(review['average']) 
        return avg
    
    def count_review(self):
        review_count = ReviewRating.objects.filter(product= self, status = True).aggregate(count = Count('id'))
        count = 0 
        if review_count['count'] is not None:
            count = int(review_count['count']) 
        return count



class ProductOffer(models.Model):
    offer_name  =models.CharField(max_length=25, blank= True, null = True)
    product = models.ForeignKey(Product, blank = True,null=True, on_delete=models.CASCADE)
    off_percentage = models.IntegerField(blank=True, null = True)
    valid_from = models.DateField(blank=True, null=True)
    valid_upto = models.DateField(blank=True, null=True)
    expired = models.BooleanField(default=True)

    def __str__(self):
        return self.offer_name

class CategoryOffer(models.Model):
    offer_name  =models.CharField(max_length=25, blank= True, null = True)
    category  = models.ForeignKey(Category, on_delete=models.CASCADE, blank= True, null = True)
    off_percentage = models.IntegerField(blank=True, null=True)
    valid_from = models.DateField()
    valid_upto = models.DateField()
    expired = models.BooleanField(default=True)

    def __str__(self):
        return self.offer_name 

class CouponCode(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True)
    coupon_name = models.CharField(max_length=6)
    off_price = models.IntegerField()
    valid_from = models.DateField()
    valid_upto  = models.DateField()
    valid = models.BooleanField(default= False)

    def __str__(self):
        return self.coupon_name

class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject =  models.CharField(max_length=100, blank = True)
    review = models.TextField(max_length=500, blank = True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject