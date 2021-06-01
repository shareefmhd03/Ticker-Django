from django import forms
from .models import Product, ProductOffer, ReviewRating


class AddProduct(forms.ModelForm):  
    class Meta:
        model     = Product
        fields    = ['product_name', 'slug', 'price', 'description', 'category', 'image1','image2', 'image3','image4','stock', 'brand','gender', 'strap_colour','water_resistance','analogue_or_digital', 'glass','strap_type','model_name'] 

    def __init__(self, *args, **kwargs):
            super(AddProduct, self).__init__(*args, **kwargs)
            self.fields['description'].widget.attrs['id'] = 'desc'
            for field in self.fields:
                self.fields[field].widget.attrs['class'] = 'form-control'     
            

class ProductOfferForm(forms.ModelForm):
    class Meta:
        model = ProductOffer
        fields = ['offer_name', 'product', 'off_percentage','valid_from','valid_upto']


class ReviewForm(forms.ModelForm):
    class Meta:
        model =  ReviewRating
        fields = ['subject', 'review', 'rating']