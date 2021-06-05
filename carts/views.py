from datetime import date
import datetime
import json
from django.contrib import messages
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from store.models import CouponCode, Coupons, Product, Category, CategoryOffer, ProductOffer

from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from accounts.models import Address
from store.models import Product


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_to_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)

    if current_user.is_authenticated:

        # is_cart_item_exists = CartItem.objects.filter(product = product).exists()

        try:
            CartItem.objects.filter(
                product=product, user=current_user).exists()
            print('add to cart ----- try block')
            cart_item = CartItem.objects.get(
                product=product, user=current_user)
            cart_item.quantity += 1
            cart_item.save()
            print(cart_item.product.product_name)
        except CartItem.DoesNotExist:
            print('in_except-cart')
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )

            cart_item.save()
        return redirect('cart')

    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()
        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1
            cart_item.save()

        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
            cart_item.save()
        return redirect('cart')


def remove_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:

            cart_item = CartItem.objects.get(
                product=product, user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def delete_cart_item(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart)

    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
            # cart = Cart.objects.filter(user = request.user, is_active = True)
            for cart_item in cart_items:
                total = cart_item.sub_total()
                # print(total, 'incart_total')
                if cart_item.product.offer_price:

                    grand_total += cart_item.product.offer_price * cart_item.quantity
                    # print(cart_item.quantity)
                    # print(grand_total,'grand total_offer_price---cart')
                else:
                    grand_total += (cart_item.product.price *
                                    cart_item.quantity)
                    # print(cart_item.quantity)
                    # print(grand_total,'grand_total_product_price---cart')
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            for i in cart_items:
                total = i.sub_total()
            for cart_item in cart_items:

                if cart_item.product.offer_price:

                    grand_total += cart_item.product.offer_price * cart_item.quantity
                    # print(grand_total,'grand total')
                else:
                    grand_total += (cart_item.product.price *
                                    cart_item.quantity)
                    # print(grand_total,'grand_total')

                quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass
    context = {
        'total': total,
        'grand_total': grand_total,
        # 'quantity': quantity,
        'cart_items': cart_items,
        # 'cart':cart,
    }

    return render(request, 'user/cart.html', context)


def coupon_confirm(request, total=0, new_price=0):
    today = date.today()
    NextDay_Date = datetime.date.today() + datetime.timedelta(days=2)
    if request.method == 'POST':
        coupon = request.POST['coupon']
        print('start')
        try:
            valid = CouponCode.objects.get(user=request.user, coupon_name=coupon,
                                           valid_from__lte=today, valid_upto__gte=NextDay_Date)
            # valid.delete()
            for val in valid:
                if val.valid == True:
                    coupon_price(request, valid.off_price)
                # print(total,'totals here')
                    val.valid = False
                    print(val.valid)
                    val.save()
                else:
                    # messages.info(request, 'invalid coupon code')
                    pass

            # request.session['coupon_id'] == coupon.id

                    # total +=(cart_item.product.price * cart_item.quantity)
                    # print(total)
                    # cart_item.product.save(update_fields  =['offer_price'])
        except CouponCode.DoesNotExist:
            # request.session['coupon_id']= None
            print('in except')
            pass
    return redirect('checkout')


def coupon_price(request, off_price):
    new_price = 0
    cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    cart = CartItem.objects.filter(user=request.user, is_active=True)
    # product = Product.objects.get(id  = cart_items.product.id)
    print('in try')
    for cart_item in cart_items:
        print('in loop2')
        if cart_item.product.offer_price:
            new_price += cart_item.product.offer_price * cart_item.quantity

            reduce = new_price * (off_price/100)
            print(reduce)
            total = new_price - reduce
            cart_item.product.coupon_price = total
            print(cart_item.product.coupon_price, 'if_---')

            cart_item.product.save(update_fields=['coupon_price'])
            print(cart_item.product.coupon_price, 'if')
            # valid.valid = False
            # valid.save()
            # return total

        else:
            print('i _else')
            new_price += (cart_item.product.price * cart_item.quantity)
            print(new_price)

            reduce = new_price * (off_price/100)
            total = new_price - reduce
            cart_item.product.coupon_price = total
            print(cart_item.product.coupon_price, 'if')
            cart_item.product.save(update_fields=['coupon_price'])
            print(cart_item.product.coupon_price, 'ifff')

            # return total


@login_required(login_url='user_login')
def checkout(request, total=0, quantity=0, cart_items=None):

    try:
        is_saved = Address.objects.filter(user=request.user).exists()
        address = Address.objects.filter(user=request.user)

    except Address.DoesNotExist:
        address = None
    try:
        # cart = Cart.objects.get(cart_id = _cart_id(request))
        # cart_items = CartItem.objects.filter(user = request.user, is_active=True)

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'address': address,
        'is_saved': is_saved,
    }
    return render(request, 'user/checkout.html', context)


def get_address(request):

    if request.method == 'GET':

        id = request.GET['address']
        print(id)

        add = Address.objects.get(id=id)

        data = {}
        data['first_name'] = add.first_name
        data['last_name'] = add.last_name
        data['email'] = add.email
        data['address'] = add.address
        data['city'] = add.city
        data['state'] = add.state
        data['phone'] = add.phone
        # return "success"
        return HttpResponse(json.dumps(data), content_type="application/json")


# Cart quantity ------------------------------------------
def add_cart(request, id):

    current_user = request.user
    value = int(request.POST['value'])
    product = Product.objects.get(id=id)
    grand_total = 0
    if current_user.is_authenticated:
        try:

            if value == 1:
                cart_item = CartItem.objects.get(
                    product=product, user=current_user)
                cart_item.quantity += 1
                cart_item.save()
                tot = cart_item.sub_total()
                grand_total += tot
                data = {'id': id, 'quantity': cart_item.quantity,
                        'total': tot, 'grand_total': grand_total}
                return JsonResponse(data=data)

            if value == -1:
                cart_item = CartItem.objects.get(
                    product=product, user=current_user)
                if cart_item.quantity >= 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                    tot = cart_item.sub_total()

                    grand_total += tot
                    if cart_item.quantity < 1:
                        cart_item.delete()

                data = {'id': id, 'quantity': cart_item.quantity,
                        'total': tot, 'grand_total': grand_total}
                return JsonResponse(data=data)

        except ObjectDoesNotExist:
            print('not exist')
            return redirect('cart')
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
            cart.save()
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart)
            if value == 1:
                cart_item.quantity += 1
                cart_item.save()
                tot = cart_item.sub_total()
                grand_total += tot
                data = {'id': id, 'quantity': cart_item.quantity,
                        'total': tot, 'grand_total': grand_total}
                return JsonResponse(data=data)

            elif value == -1:
                if cart_item.quantity >= 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                    tot = cart_item.sub_total()

                    grand_total += tot
                    if cart_item.quantity < 1:
                        cart_item.delete()
                data = {'id': id, 'quantity': cart_item.quantity,
                        'total': tot, 'grand_total': grand_total}
                return JsonResponse(data=data)

        except CartItem.DoesNotExist:
            return redirect('cart')


def coupon_verify(request, total=0, new_price=0):
    if request.method == 'POST':
        coupon = request.POST['coupon']
        print('start')
        try:
            valid = Coupons.objects.filter(coupon_name=coupon)

            for val in valid:
                print(val.valid)
                if val.valid == True:
                    coupon_price(request, val.off_price)
                # print(total,'totals here')
                    val.valid = False
                    print(val.valid)
                    val.save()

        except CouponCode.DoesNotExist:

            print('in_except')

        try:
            valid = CouponCode.objects.filter(
                user=request.user, coupon_name=coupon)
            print('hai')

            for val in valid:
                if val.valid == True:
                    coupon_price(request, val.off_price)
                # print(total,'totals here')
                    val.valid = False
                    print(val.valid)
                    val.save()
                    messages.success(request, 'Coupon Applied')
                else:
                    messages.info(request, 'invalid coupon ')

        except CouponCode.DoesNotExist:

            print('in except')

    return redirect('checkout')


def validate_coupon(request):

    code = str(request.GET.get('code'))
    print(code)
    print('in validate coupon')
    data = {
        'valid': Coupons.objects.filter(coupon_name=code, valid=True).exists(),
        'val': CouponCode.objects.filter(user=request.user, coupon_name=code, valid=True).exists(),
    }
    print(data['valid'])

    return JsonResponse(data)
