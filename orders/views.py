from carts.views import coupon_price
from accounts.models import Address
from store.models import Product
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from carts.models import CartItem
from .forms import OrderForm
from .models import Order,OrederProduct, Payment
import datetime
import json
# import razorpay
# from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def razorpay_payment(request,pk):
    
    if request.method == 'POST':
        order = Order.objects.get(user =request.user, is_ordered=False, id=pk)
         
        payment_method = 'RazorPay'
        payment        = Payment(
                user           = request.user,
                payment_method = payment_method,
                status         = 'completed'
        )
        
        payment.save()
        order.payment = payment
        order.is_ordered =True
        order.save()

        cart_items = CartItem.objects.filter(user = request.user)
        for item in cart_items:
            order_product          = OrederProduct()
            order_product.order_id = order.id
            order_product.payment  = payment
            order_product.user     = request.user
            order_product.product  = item.product
            order_product.quantity = item.quantity
            order_product.product_price = item.product.price
            order_product.ordered  = True
            order_product.save()

            product = Product.objects.get(id= item.product.id)
            product.stock -= item.quantity
            print(product.stock)
            product.save()
        
            if item.product.coupon_price:
                item.product.coupon_price= None
                item.product.save()
        cart_items = CartItem.objects.filter(user = request.user).delete()

        return redirect('razor_success', pk = order.id)
  
    
def razor_success(request,pk):
    try:
        order = Order.objects.get(user =request.user, is_ordered=True, id=pk)
        print('passed1')
        order_number = order.order_no
        print('passed2')
        ordered_products = OrederProduct.objects.filter(order_id = order.id)
        print('passed3')
        # payment   = Payment.objects.get(payment_id = order_number)
        print('here')
        subtotal = 0

        for i in ordered_products:
            if i.product.offer_price:
                subtotal += i.product.offer_price * i.quantity
            else:
                subtotal += i.product.price * i.quantity

        print('passed4')
        context ={
            'order'            :order,
            'ordered_products' :ordered_products,
            'order_number'     :order.order_no,
            # 'transID'          :payment.payment_id,
            # 'payment'          :payment,
            'subtotal'         :subtotal,
        }
        print('success url here')
        return render(request, 'user/razor_success.html', context)


    except (Payment.DoesNotExist, Order.DoesNotExist):
            print('except case')
            return redirect('home')
            





def success(request):
    try:
        order_number = request.GET.get('order_number')
        transID      = request.GET.get('payment_id')
        order            = Order.objects.get(order_no = order_number, is_ordered = True)               
        ordered_products = OrederProduct.objects.filter(order_id = order.id)
        payment          = Payment.objects.get(payment_id = transID)
       
        subtotal = 0

        for i in ordered_products:
            subtotal += i.product_price * i.quantity


        context ={
            'order'            :order,
            'ordered_products' :ordered_products,
            'order_number'     :order.order_no,
            'transID'          :payment.payment_id,
            'payment'          :payment,
            'subtotal'         :subtotal,
        }
        print('success url here')
        return render(request, 'user/success.html', context)


    except (Payment.DoesNotExist, Order.DoesNotExist):
        print('except case')
        return redirect('home')
    




def pay_payments(request):
    print('order now')
    body                = json.loads(request.body)
    order               = Order.objects.get(user = request.user, is_ordered = False, order_no = body['orderID'])
    payment             = Payment(
            user           = request.user,
            payment_id     = body['transID'],
            payment_method = body['payment_method'],
            amount_paid    = float(order.order_total)/70,
            status         = body['status'],

    )
    payment.save()
    order.payment    = payment
    order.is_ordered = True
    order.status = 'completed'
    order.save()
    print('order successful')
    print(order.status)

    cart_items = CartItem.objects.filter(user = request.user)
    for item in cart_items:
        order_product               = OrederProduct()
        order_product.order_id      = order.id
        order_product.payment       = payment
        order_product.user_id       = request.user.id
        order_product.product_id    = item.product_id
        order_product.quantity      = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered       = True
        order_product.save()

        product = Product.objects.get(id = item.product_id)
        product.stock -=item.quantity
        
        product.save()

        if item.product.coupon_price:
                item.product.coupon_price= None
                item.product.save()

    
    cart_items = CartItem.objects.filter(user = request.user).delete()

    
    print('cart items deleted')
    data = {
        'order_number' : order.order_no,
        'transID'      : payment.payment_id
    }  
    return JsonResponse(data)
   






def payments(request ,pk):  
    if request.method == 'POST':
        
        order = Order.objects.get(user =request.user, is_ordered=False,id=pk)
         
        payment_method = 'COD'
        payment        = Payment(
                user           = request.user,
                payment_method = payment_method,
                status         = 'pending'
        )
        
        payment.save()
        order.payment = payment
        order.is_ordered =True
        order.save()

        cart_items = CartItem.objects.filter(user = request.user)
        for item in cart_items:
            order_product          = OrederProduct()
            order_product.order_id = order.id
            order_product.payment  = payment
            order_product.user     = request.user
            order_product.product  = item.product
            order_product.quantity = item.quantity
            order_product.product_price = item.product.price
            order_product.ordered  = True
            order_product.save()

            product = Product.objects.get(id= item.product.id)
            product.stock -= item.quantity
            print(product.stock)
            
            product.save()

            if item.product.coupon_price:
                item.product.coupon_price= None
                item.product.save()
        
            
        cart_items = CartItem.objects.filter(user = request.user).delete()

        return redirect('razor_success',pk = order.id)
    return redirect('payments')


def confirm_order(request, pk):
    order = Order.objects.get(id=pk)
    
    if order.is_ordered == False:

        order.is_ordered =True
        order.status     = 'confirmed'
        order.save()

    return redirect('order_management')


def cancel_order(request, pk): 

    order  = Order.objects.get(id=pk) 
    oreder = OrederProduct.objects.filter(order= order.id)  

    if order.is_ordered == True:

        order.is_ordered = False
        order.status     = 'cancelled' 
        order.save()

        for ord in oreder:
            ord.product.stock += ord.quantity
            ord.product.save()
    
    return redirect('order_management')


def place_order(request, total=0, quantity =0):
    current_user = request.user
   
    # address = Address.objects.get(user = current_user)
    cart_items =CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')


    grand_total = 0
    for cart_item in cart_items:
            
        if cart_item.product.offer_price:
            if cart_item.product.coupon_price:
                total += cart_item.product.coupon_price * cart_item.quantity
                print(total,'if')
            else:
                total += cart_item.product.offer_price * cart_item.quantity
                print(total,'if')
        elif  cart_item.product.coupon_price:              
                total += cart_item.product.coupon_price * cart_item.quantity
                print(total,'if')
        else:
            total +=(cart_item.product.price * cart_item.quantity)
            print(total)
        paypal_total   = int(total/70)
        print(paypal_total)
        razorpay_total = total*100
        quantity += cart_item.quantity

    if request.method == 'POST':

        form = OrderForm(request.POST)

        if form.is_valid():
            data             = Order()
            data.user        = current_user
            data.first_name  = form.cleaned_data['first_name']
            data.last_name   = form.cleaned_data['last_name']
            data.email       = form.cleaned_data['email']
            data.phone       = form.cleaned_data['phone']
            data.address     = form.cleaned_data['address']
            data.city        = form.cleaned_data['city']
            data.state       = form.cleaned_data['state']
            data.order_total = total
            data.ip          = request.META.get('REMOTE_ADDR')
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d  = datetime.date(yr,mt,dt)
            current_date = d.strftime('%Y%m%d')
            
            order_number = current_date + str(data.id)
            
            data.order_no = order_number
            data.save()

            order = Order.objects.get(user =current_user, is_ordered = False, order_no= order_number)
            context = {
                'order'         : order,
                'total'         : total,
                'cart_items'    :cart_items,
                'paypal_total'  :paypal_total,
                'razorpay_total':razorpay_total,

            }
            return render(request, 'user/payments.html', context)
    else:
        return redirect('checkout')



def orders_details(request):

    current_user = request.user
    ord = OrederProduct.objects.filter(user =current_user)
    
    context ={
        'order':ord,
        'user' :current_user,
    }  
    return render(request, 'user/orders_details.html', context)


def cancel_order_user(request,pk):

    order  = Order.objects.get(id=pk , user =request.user) 
    oreder = OrederProduct.objects.filter(order= order.id)  

    if order.is_ordered == True:

        order.is_ordered = False
        order.status     = 'cancelled by user' 
        order.save()

        for ord in oreder:
            ord.product.stock += ord.quantity
            ord.product.save()
    return redirect('orders_details')