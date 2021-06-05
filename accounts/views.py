import base64
from typing import Counter
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from orders.models import Order, OrederProduct
from django.db.models import query
from django.db.models.query_utils import Q
from django.http.response import HttpResponse
from store.models import CouponCode, Product
from carts.models import Cart, CartItem
from django.shortcuts import render,redirect
from django.contrib.sessions.models import Session
from .forms import ProfileForm, ProfileImage, RegistrationForm, AddressForm
from .models import Account, Address, Profile
from django.contrib import auth, messages
from django.contrib.auth import logout,login,authenticate
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse 
from carts.views import _cart_id
from django.contrib.auth.tokens import default_token_generator
from django.core.paginator import Paginator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
import requests
import twilio
from twilio.rest import Client
import random
import datetime




def session_check(request):
    if  request.session['loggedin']== True:
        return True

    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home') 
    if request.method == 'POST':
        email    = request.POST['email']
        password = request.POST['password']
        user     = auth.authenticate(request, email = email, password = password)

        use = Account.objects.get(email = email)
        if use.is_active == False:
               messages.info(request, use.first_name +' is blocked')
               return redirect('user_login')
        count = 1
        counter = 1
        if user is not None:
            try:

                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_items_exists = CartItem.objects.filter(cart = cart).exists()
                print(is_cart_items_exists)

                if is_cart_items_exists: 
                    cart_item = CartItem.objects.filter(cart = cart)
                    print('after fetching cart')
                    cart_prod = []
                    for item in cart_item:
                        print('in_for_1')
                        prod = item.product_id
                        print('products are fetched')
                        cart_prod.append(prod)
                    print(cart_prod)
                    

                    cart_item = CartItem.objects.filter(user = user)
                    ex_prod = []
                    id =[]
                    for item in cart_item:
                        print('in_for_2')
                        existing_prod = item.product_id
                        ex_prod.append(existing_prod)
                        
                        id.append(item.id) 
                    print(ex_prod)


                    for cp in cart_prod:
                        print('in_for_3')
                        if cp in ex_prod:
                            index = ex_prod.index(cp)
                            item_id = id[index]
                            item =CartItem.objects.get(id = item_id)
                            item.quantity+=1
                            item.user = user          
                            item.save()
                        else:
                            print('in_else')
                            cart_item = CartItem.objects.filter(cart = cart)
                            for item in cart_item:                               
                                item.user = user             
                                item.save()
            
                            
         
                               
                
            
            except:
                pass


            auth.login(request, user)
            url = request.META.get('HTTP_REFERER')
            print(url)
            try:
                query = requests.utils.urlparse(url).query
                # print('query')
                params = dict(x.split('=') for x in query.split('&'))
                # print(params)
                if 'next'  in params:
                    next_page =  params['next']
                    return redirect(next_page)
                  
            except:
                return redirect('home')  
               
        else:   
            messages.info(request,'invalid credentials')
            return redirect('user_login')
    return render(request, 'user/login.html')
    

def profile_view(request, ref_code):
    ref_id = ref_code
    try:
        profile = Profile.objects.get(code = ref_id)
        request.session['ref_profile'] = profile.id
        request.session['coupon_session']== True
    except:
        pass


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_register(request, *args, **kwargs):
    today = datetime.date.today()
    third_day = today+ datetime.timedelta(days=3)
    if request.method == 'POST':
        
        form   = RegistrationForm(request.POST)
        if form.is_valid():
            firstname  = form.cleaned_data['first_name']
            lastname   = form.cleaned_data['last_name']
            email      = form.cleaned_data['email']
            phone      = form.cleaned_data['phone']
            password   = form.cleaned_data['password']
            ref_code   = form.cleaned_data['referral']

            
            profile_view(request, ref_code)  
            user       = Account.objects.create_user(first_name = firstname, last_name = lastname, email = email, password = password)
            user.phone = phone

            profile_id = request.session.get('ref_profile')  
            # coupon_session = request.session.has_key('coupon_session')
            
            if profile_id is not None:
                recommended_by_profile = Profile.objects.get(id = profile_id)
                recom_user = recommended_by_profile.user
                print(recom_user)
  
                user.save()
                registered_user = Account.objects.get(id = user.id) 
                registered_profile = Profile.objects.get(user = registered_user)
                registered_profile.recommended_by= recommended_by_profile.user
                registered_profile.save()

                coupon_name = 'off50'
                offer_price = 50
                coupon = CouponCode.objects.create(user = user, coupon_name = coupon_name, off_price = offer_price, valid_from =today, valid_upto=third_day, valid= True)
                coupon2 = CouponCode.objects.create(user = recom_user, coupon_name = coupon_name, off_price = offer_price, valid_from =today, valid_upto=third_day, valid= True)
                coupon.save()
                coupon2.save()
    
                del request.session['ref_profile']
            # else:
                # messages.info(request, 'invalid referral code')
                # return redirect('user_register')
                
        # print(request.session.get_expiry_date())
        user.save()
        return redirect('user_login')
    else:
        form = RegistrationForm 

    context  = {
        'form': form
    }
    return render(request, 'user/register.html', context)


def validate_referralcode(request):
    
    code = str(request.GET.get('code'))
    
    data = {
        'valid': Profile.objects.filter(code= code).exists()
    }    
    if data['valid']:
        data['error_message'] = 'Invalid referal code'
    
    return JsonResponse(data)

def forgot_password(request):

    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email = email).exists():
            user  = Account.objects.get(email__exact = email)
            current_site = get_current_site(request)
            mail_subject = 'reset_password'
            message = render_to_string('user/reset_password_email.html',{
               'user' :user,
               'domain' :current_site,
               'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
               'token':default_token_generator.make_token(user),

            })

            to_email = email
            send_email = EmailMessage(mail_subject, message, to =[to_email])
            send_email.send()


            messages.success(request, 'password reset email has been send')
            return redirect('user_login')
        else:
            messages.error(request, 'Account not exist')
            return redirect('forgot_password')

    return render(request, 'user/forgot_password.html')
    


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
         
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']  = uid
        messages.success(request, 'Please reset your password')
        return redirect('reset_password')

    else:
        messages.error(request, 'This link has been Expired')
        return redirect('user_login')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
         
        if password == confirm_password:
            uid= request.session.get('uid')
            user = Account.objects.get(pk = uid)
            user.set_password(password)
            user.save()

            messages.success(request, 'Password reset successful')
            return redirect('user_login')

        else:
            messages.error(request, 'passwords do not match') 
            return redirect('reser_password')
    else:
        return render(request, 'user/reset_password.html')



# ajax validation-----------------------------
def validate_email(request):

    email = request.GET.get('email', None)
    print(email)
    data = {
        'is_taken': Account.objects.filter(email= email).exists()
    }    
    if data['is_taken']:
        data['error_message'] = 'A user with this email already exists.'
    return JsonResponse(data)



def user_profile(request, id):
    if request.user.is_authenticated:
        user = Account.objects.get(id= id)
     
        try:
            is_saved = Address.objects.filter(user=request.user, user_id = id).exists()
            address = Address.objects.filter(user=request.user, user_id = id)
            
                    
        except Address.DoesNotExist:  
            
            address = None
        try:  
            img = Profile.objects.get(user = request.user)
            print(img.code)
            my_recs = img.get_recommended_profiles()
            # image = img.profile_image

        except Profile.DoesNotExist:
                img = None
        try:
            coupon = CouponCode.objects.filter(user = request.user, valid = True)
            print(coupon)

        except CouponCode.DoesNotExist:
            coupon= None

        context = {
                'user':user,
                'address':address,
                'is_saved': is_saved,
                'img':img,
                'my_recs':my_recs,
                'coupon':coupon,
            }
        return render(request, 'user/user_profile.html', context)
    return redirect('login')


# def user_profile_coupons(request, id):
#     if request.user.is_authenticated:
#         user = Account.objects.get(id= id)
        
       
       

#         context = {
#                 'user':user,
#                 'coupon':coupon,
#             }
#         return render(request, 'user/referal.html', context)
#     return redirect('login')


def profile_image(request):
    if request.user.is_authenticated:

        if request.method == 'POST':
            user = request.user
            
            # img = request.FILES.get('profile_image')
            image1       = request.POST['pro_img1']
            if Profile.objects.filter(user = request.user).exists():
                prof_image = Profile.objects.get(user = request.user)
                

                format, img1 = image1.split(';base64,')
                ext = format.split('/')[-1]
                img_data1 = ContentFile(base64.b64decode(img1), name= user.first_name + '1.' + ext)
                prof_image.profile_image = img_data1
                prof_image.save()
                return redirect('user_profile', id = user.id)
                
            else:
                format, img1 = image1.split(';base64,')
                ext = format.split('/')[-1]
                img_data1 = ContentFile(base64.b64decode(img1), name= user.first_name + '1.' + ext)
                
                prof_image = Profile(user = request.user, profile_image =img_data1)
                prof_image.save()
               
        return render(request, 'user/user_profile.html')
    return redirect('user_login')

def edit_profile(request, id):
    if request.user.is_authenticated:
        
        user = Account.objects.get(id = id)
        form = ProfileForm(instance=user)
        if request.method == 'POST':
            form   = ProfileForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                return redirect('home')
        
        context  = {
            'form': form,           
        }
        return render(request, 'user/edit_profile.html', context)
    return redirect('login')



def add_address(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method =='POST':
            form   = AddressForm(request.POST)
            if form.is_valid():
                firstname  = form.cleaned_data['first_name']
                lastname   = form.cleaned_data['last_name']
                email      = form.cleaned_data['email']
                phone      = form.cleaned_data['phone']
                address    = form.cleaned_data['address']
                city       = form.cleaned_data['city']
                state      = form.cleaned_data['state']
                
                address      = Address(user =request.user, first_name = firstname, last_name = lastname, email = email, phone = phone, address = address, state = state, city= city)
                address.save()
                return redirect('user_profile', user.id)
        else:
            form = AddressForm 
        context  = {
            'form': form
        }
        return render(request, 'user/add_address.html', context)
    return redirect('user_login')
    
def add_address_in_checkout(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method =='POST':
            form   = AddressForm(request.POST)
            if form.is_valid():
                firstname  = form.cleaned_data['first_name']
                lastname   = form.cleaned_data['last_name']
                email      = form.cleaned_data['email']
                phone      = form.cleaned_data['phone']
                address    = form.cleaned_data['address']
                city       = form.cleaned_data['city']
                state      = form.cleaned_data['state']
                
                address      = Address(user =request.user, first_name = firstname, last_name = lastname, email = email, phone = phone, address = address, state = state, city= city)
                address.save()
                return redirect('checkout')
        else:
            form = AddressForm 
        context  = {
            'form': form
        }
        return render(request, 'user/add_address.html', context)
    return redirect('user_login')



def edit_address(request,id):
    if request.user.is_authenticated:
        user = request.user
        address = Address.objects.get(user=request.user, id =id)
        form    = AddressForm(instance= address)

        if request.method == 'POST':
            form = AddressForm(request.POST, request.FILES, instance= address)
            
            if form.is_valid():
                form.save()
                return redirect('user_profile',user.id)
        context  = {
            'form': form,     
        }
        return render(request, 'user/edit_address.html', context)
    return redirect('user_login')

def edit_address_in_checkout(request,id):
    if request.user.is_authenticated:
        user = request.user
        address = Address.objects.get(user=request.user, id =id)
        form    = AddressForm(instance= address)

        if request.method == 'POST':
            form = AddressForm(request.POST, request.FILES, instance= address)
            
            if form.is_valid():
                form.save()
                return redirect('checkout')
        context  = {
            'form': form,     
        }
        return render(request, 'user/edit_address.html', context)
    return redirect('user_login')


def delete_address(request, id):
    user = request.user
    address = Address.objects.get(id=id)
    address.delete()
    return redirect('user_profile', user.id)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_view(request):
    logout(request)
    request.session['loggedin'] = True
    return redirect ('home')




# adminpage--------------------------------------------------------
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    if request.method == 'POST':
        # use  = 'admin@admin.com'
        # pswd = '123'  
        username = request.POST['email']
        password = request.POST['password']

        # if username == use and password == pswd:
        #     request.session['loggedin'] = True          
        try:   # return redirect( 'admin_home')
            user = auth.authenticate(request, email = username, password = password)

            use = Account.objects.get(email = username)

            if use.is_admin == False:
                return redirect( 'admin_login')

            if user is not None:
                request.session['loggedin'] = True 
                return redirect( 'admin_home')
            else:
                return redirect('admin_login')
        except:
            pass

    
    return render(request, 'admin/admin_login.html')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_home(request):
    if session_check(request):
        today =datetime.date.today()
        month =today.month
        order =Order.objects.filter( is_ordered = True, status = 'completed',)
        order_cancel=Order.objects.filter( is_ordered = False, status = 'cancelled',)
        order_pend=Order.objects.filter( is_ordered = True, status = 'pending',)
        order_place= Order.objects.filter( is_ordered = True, status = 'Order placed',)
        order_complete  = order.count()
        order_cancelled  = order_cancel.count()
        order_pending  = order_pend.count()
        order_placed  =order_place.count()
        print('--------')
        print('asasasas',order_placed)
        print('--------')
        print(order_complete)

        # users = Account.objects.exclude(is_superadmin = 1, is_admin = 1).order_by('-id')
        users = Account.objects.filter(date_joined__lte=datetime.datetime.today(), date_joined__gt=datetime.datetime.today()-datetime.timedelta(days=7))
        paginator = Paginator(users,4)
        page = request.GET.get('page')
        paged_user = paginator.get_page(page) 
        user_count = users.count()
        
        total_profit =0
        sales_today = Order.objects.filter( is_ordered = True,created_at__lte=datetime.datetime.today(), created_at__gt=datetime.datetime.today()-datetime.timedelta(days=7))
        # sales_today =Order.objects.filter(is_ordered = True, created_at__date = today)
        print(today.month)
        for sales in sales_today:
            print(sales.created_at)
            total_profit  += sales.order_total
        sales_today_ = sales_today.count()
        
        print(sales_today_)
        print(total_profit)
        
        # new_users = A.objects.filter(date_joined__month=datetime.now().month).count()

        day1=datetime.datetime.today().day
        print('a=',day1)
        day2=day1-1
        day3=day2-1
        day4=day3-1
        day5=day4-1
        day6=day5-1
        day7=day6-1

        day1_order =Order.objects.filter(created_at__day=day1).count()
        day2_order =Order.objects.filter(created_at__day=day2).count()
        day3_order =Order.objects.filter(created_at__day=day3).count()
        day4_order =Order.objects.filter(created_at__day=day4).count()
        day5_order =Order.objects.filter(created_at__day=day5).count()
        day6_order =Order.objects.filter(created_at__day=day6).count()
        day7_order =Order.objects.filter(created_at__day=day7).count()


        sales =Order.objects.filter(is_ordered = True).order_by('-created_at')
        paginator = Paginator(sales,4)
        page = request.GET.get('page')
        paged_order = paginator.get_page(page)
        sales_count = sales.count() 

        context = {
            'sales':paged_order,
            'users':paged_user,
            'user_count':user_count,
            'sales_count':sales_count,
            'order_complete':order_complete,
            'order_cancelled':order_cancelled,
            'order_pending':order_pending,
            'order_placed':order_placed,
            'total_profit': total_profit,
            # 'items':items,
            'day1':day1_order,
            'day2':day2_order,'day3':day3_order,'day4':day4_order,'day5':day5_order,'day6':day6_order,'day7':day7_order

        }
        return render(request, 'admin/admin_home.html', context)
    return redirect('admin_login')
    



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_logout(request):
    del request.session['loggedin']
    return redirect('admin_login')





def otp_login(request):
    if request.method=='POST':
        phone=request.POST['phone']
        if Account.objects.filter(phone=phone).exists():
            otp = random.randint(100000,999999)
            strotp=str(otp)
            account_sid ='AC2ceccd0b4c15e5d74f012550232f80b7'
            auth_token ='580e4199348168f8dad6ec879bc643eb'
            client = Client(account_sid, auth_token)

            message = client.messages \
                .create(
                     body="Your login OTP is"+strotp,
                     from_='+13012816882',
                     to='+91'+phone
                 )
            request.session['otp']=otp
            print(request.session['otp'])
            request.session['phone']=phone
            print(request.session['phone'])
            print(otp,phone)
            messages.success(request,"OTP Sended Successfully")
            return redirect('verify_otp')  
        messages.error(request,"enter valid phone number")    
        return redirect('otp_login')    

    return render(request,'user/otplogin.html')


def verify_otp(request):
    if request.method=='POST':
        enter_otp=request.POST['otp']
        otp=int(enter_otp)
        if request.session.has_key('otp'):
            sended_otp=request.session['otp']
         
            
            if sended_otp == otp :
                print("in if")
                phone=request.session['phone']
                print(phone)
                user=Account.objects.get(phone=phone)
                login(request,user)
                del request.session['otp']
                del request.session['phone']
                
                return redirect('home')
            else:    
                messages.error(request,"entered OTP is wrong")
                return redirect('otp_login') 
        else:
            return redirect('otp_login')          
    return render(request,'user/verifyotp.html')



def referrals(request):
    ref = Profile.objects.get(user = request.user)
    valid = CouponCode.objects.filter(user = request.user, valid = True).exists()
    print(valid)
    try:
        coupon = CouponCode.objects.filter(user = request.user, valid = True)
            # print(coupon.coupon_name)
    except CouponCode.DoesNotExist:
        coupon = None
    print('here')
    print(ref.code)
    ref_code  = ref.code
    myrecs = ref.get_recommended_profiles()

    context = {
        'myrecs':myrecs,
        'ref_code':ref_code,
        'coupon':coupon,
        'valid':valid,
    }
    return render(request, 'user/referal.html', context)
