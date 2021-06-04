from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.deletion import CASCADE
from django.urls import reverse
from .utils import generate_ref_code




class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, password = None):
        if not email:
            raise ValueError("Email is required")

        user = self.model(
            email       = self.normalize_email(email),
            first_name  = first_name,
            last_name   = last_name,
    
            
        )
        user.is_active     = True
        user.set_password(password)
        user.save()
        return user



    def create_superuser(self, first_name, last_name, email, password,):
        user = self.create_user(
            email       = self.normalize_email(email),
            first_name  = first_name,
            last_name   = last_name,
            password    = password,


        ) 
        user.is_admin      = True
        user.is_active     = True
        user.is_staff      = True
        user.is_superadmin = True
        user.save()
        return user 


        
class Account(AbstractBaseUser):
     first_name     = models.CharField(max_length=50)
     last_name      = models.CharField(max_length=50)
     email          = models.EmailField(max_length=50, unique=True)
     phone          = models.CharField(max_length=20)
     referral        = models.CharField(max_length=12, blank = True)
     
     date_joined    = models.DateTimeField(auto_now_add=True)
     last_login     = models.DateTimeField(auto_now_add=True)
     is_admin       = models.BooleanField(default=False)
     is_staff       = models.BooleanField(default=False)
     is_active      = models.BooleanField(default=False)
     is_superadmin  = models.BooleanField(default=False)


     USERNAME_FIELD = 'email'
     REQUIRED_FIELDS = ['first_name', 'last_name']  

     objects = MyAccountManager()


     def __str__(self):
         return self.email

     def has_perm(self, perm, obj=None):
         return self.is_admin
    
     def has_module_perms(self, add_abel):
         return True

     def get_user(self):
         return reverse('user_profile', args =[self.id])


class Address(models.Model):
    user  =models.ForeignKey(Account, on_delete=CASCADE, blank = True, null= True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)

    def __str__(self):
        return self.first_name



class Profile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to="profile_images", default = "default.jpeg")
    code = models.CharField(max_length=12, blank = True)
    recommended_by = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True, related_name='ref_by')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True, blank = True, null=True)

    def __str__(self):
        return self.user.first_name

    def get_recommended_profiles(self):
        qs = Profile.objects.all()
        my_recs = [p for p in qs if p.recommended_by == self.user]
        return my_recs
        # pass

        # my_recs = []
        # for profile in qs:
        #     if profile.recommended_by == self.user

    def save(self, *args, **kwargs):
        if self.code == "":
            code = generate_ref_code()
            self.code = code
        super().save(*args, **kwargs)