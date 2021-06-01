from django import forms
from django.db import models
from django.db.models import fields
from .models import Account, Address, Profile



class RegistrationForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput(attrs = {'placeholder': 'Password', 'class' : 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs = {'placeholder': 'confirm Password', 'class' : 'form-control'}))

    class Meta:
        model     = Account
        fields    = ['first_name', 'last_name', 'email','phone','referral', 'password']
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Firstname'
        self.fields['last_name'].widget.attrs['placeholder']  = 'Lastname'
        self.fields['email'].widget.attrs['placeholder']      = 'Email'
        self.fields['phone'].widget.attrs['placeholder']      = 'Phone Number'
        self.fields['email'].widget.attrs['id']               = 'email'
        self.fields['referral'].widget.attrs['placeholder']    = 'Referral Code'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data      = super(RegistrationForm, self). clean()
        password          = cleaned_data.get('password')
        confirm_password  = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                '*Passwords are not same!'
            )



class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'state', 'city']

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'  


class ProfileImage(forms.ModelForm):
    class Meta: 
        model= Profile
        fields = ['profile_image'] 
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Account
        fields    = ['first_name', 'last_name','phone']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'     
        

