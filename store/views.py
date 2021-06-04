from django.contrib.auth.models import AnonymousUser
from django.http.response import HttpResponse
from orders.models import Order, OrederProduct
from django.shortcuts import render, get_object_or_404, redirect
from . models import Coupons, Product, ProductOffer, CategoryOffer, ReviewRating
from category.models import Category
from carts.views import _cart_id
from carts.models import Cart, CartItem
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from accounts.models import Account
from .forms import AddProduct, ProductOfferForm, ReviewForm
from django.db.models import Q
import datetime
from datetime import date, timedelta, timezone
from accounts.views import session_check
import base64
from django.core.files.base import ContentFile
# Create your views here.


def store(request, category_slug=None):

    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=categories, is_available=True).order_by('id')
        paginator = Paginator(products, 10)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()  # No. of products
    context = {
        "product": paged_products,
        "count": product_count,
    }
    return render(request, 'user/store.html', context)


def product_view(request, category_slug, product_slug):
    try:
        product_exist = ProductOffer.objects.filter(
            product__slug=product_slug, expired=True).exists()

        if product_exist:
            product_off = ProductOffer.objects.filter(
                product__slug=product_slug, expired=True).exists()
            today = date.today()
            today1 = today.strftime("%Y-%m-%d")

            for offer in product_off:

                if str(offer.valid_upto) > today1:
                    pro = Product.objects.get(id=offer.product.id)
                    pro.offer_price = None
                    pro.expired = False
                    pro.save()

                else:
                    if str(offer.valid_from) > today1:
                        pro = Product.objects.get(id=offer.product.id)
                        pro.offer_price = None
                        pro.expired = False
                        pro.save()
        elif CategoryOffer.objects.filter(expired=True).exists():
            category_off = CategoryOffer.objects.filter(expired=True)
            today = date.today()
            print(today)
            today1 = today.strftime("%Y-%m-%d")
            for offer in category_off:

                if str(offer.valid_upto) > today1:
                    # val = Product..objects.get(categoy_id = offer.category_id)
                    pro = Product.objects.filter(category_id=offer.category.id)
                    for pro in pro:
                        pro.offer_price = None
                        pro.expired = False
                        pro.save()
                else:
                    if str(offer.valid_from) > today1:
                        pro = Product.objects.get(
                            category_id=offer.category.id)
                        pro.offer_price = None
                        pro.expired = False
                        pro.save()

    except ProductOffer.DoesNotExist or CategoryOffer.DoesNotExist:
        pass

    try:
        product_view = Product.objects.get(
            category__slug=category_slug, slug=product_slug)
        category_view = Category.objects.get(slug=category_slug)

        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=product_view).exists()
        try:
            product_offer_exists = ProductOffer.objects.filter(
                product=product_view.id).exists()
            category_offer_exists = CategoryOffer.objects.filter(
                category=category_view.id).exists()
        except ProductOffer.DoesNotExist and CategoryOffer.DoesNotExist:
            pass

    except Exception as e:
        raise e

    try:
        user = request.user if type(
            request.user) is not AnonymousUser else None

        print('in____try')
        order_product = OrederProduct.objects.filter(
            user__id=user.id, product_id=product_view.id).exists()
        print(order_product)

    except OrederProduct.DoesNotExist:
        print('in______except')
        order_product = None

    reviews = ReviewRating.objects.filter(
        product_id=product_view.id, status=True)

    context = {
        "prod": product_view,
        'in_cart': in_cart,
        'product_offer_exists': product_offer_exists,
        'category_offer_exists': category_offer_exists,
        'order_product': order_product,
        'reviews': reviews,
    }

    return render(request, 'user/product_View.html', context)


# user management-------------------------------------------------------
def user_management(request):
    if session_check(request):
        users = Account.objects.exclude(is_superadmin=1).order_by('id')
        return render(request, 'admin/user_management.html', {'user': users})
    return redirect('admin_login')


def del_user(request, pk):
    user = Account.objects.get(id=pk)
    user.delete()
    return redirect('user_management')


def block_user(request, pk):
    user = Account.objects.get(id=pk)
    if user.is_active == True:
        user.is_active = False
    else:
        user.is_active = True

    user.save()
    return redirect('user_management')
# end user management-----------------------------------------------------


# product management-----------------------------------------------------------------
def product_management(request):
    if session_check(request):
        product = Product.objects.all().order_by('-id')

        # prod_filter = ProductFilter(request.GET, queryset = product)

        return render(request, 'admin/product_management.html', {'product': product})
    return redirect('admin_login')


def edit_product(request, slug):
    if session_check(request):

        cat = Category.objects.all()
        product = Product.objects.get(slug=slug)
        form = AddProduct(instance=product)

        if request.method == 'POST':
            form = AddProduct(request.POST, request.FILES, instance=product)

            if form.is_valid():
                form.save()
                return redirect('product_management')

        return render(request, 'admin/update_product.html', {'form': form, 'categ': cat})
    return redirect('admin_login')


def add_product(request):
    if session_check(request):
        form = AddProduct()
        cat = Category.objects.all()
        if request.method == 'POST':
            form = AddProduct(request.POST, request.FILES)
            if form.is_valid():
                p_name = form.cleaned_data['product_name']
                slug = form.cleaned_data['slug']
                price = form.cleaned_data['price']
                image1 = request.POST['pro_img1']
                image2 = request.POST['pro_img2']
                image3 = request.POST['pro_img3']
                image4 = request.POST['pro_img4']
                description = form.cleaned_data['description']
                category = request.POST['category']
                stock = form.cleaned_data['stock']
                brand = form.cleaned_data['brand']
                gender = form.cleaned_data['gender']
                strap_colour = form.cleaned_data['strap_colour']
                water_resistance = form.cleaned_data['water_resistance']
                analogue_or_digital = form.cleaned_data['analogue_or_digital']
                glass = form.cleaned_data['glass']
                strap_type = form.cleaned_data['strap_type']
                model_name = form.cleaned_data['model_name']

                format, img1 = image1.split(';base64,')
                ext = format.split('/')[-1]
                img_data1 = ContentFile(base64.b64decode(
                    img1), name=p_name + '1.' + ext)

                format, img2 = image2.split(';base64,')
                ext = format.split('/')[-1]
                img_data2 = ContentFile(base64.b64decode(
                    img2), name=p_name + '2.' + ext)

                format, img3 = image3.split(';base64,')
                ext = format.split('/')[-1]
                img_data3 = ContentFile(base64.b64decode(
                    img3), name=p_name + '3.' + ext)

                format, img4 = image4.split(';base64,')
                ext = format.split('/')[-1]
                img_data4 = ContentFile(base64.b64decode(
                    img4), name=p_name + '4.' + ext)

                product = Product(product_name=p_name, slug=slug, price=price, image1=img_data1, image2=img_data2, image3=img_data3, image4=img_data4, description=description, category_id=category, stock=stock,
                                  brand=brand, gender=gender, strap_colour=strap_colour, water_resistance=water_resistance, analogue_or_digital=analogue_or_digital, glass=glass, strap_type=strap_type, model_name=model_name)

                product.save()
                return redirect('product_management')
            print('invalid user')
        return render(request, 'admin/add_product.html', {'form': form, 'categ': cat})
    return redirect('admin_login')


def del_product(request, pk):
    if session_check(request):
        prod = Product.objects.get(id=pk)
        prod.delete()
        return redirect('product_management')
    return redirect('admin_login')
# end Product management-----------------------------------------------------


# order management---------------------------------------------------------
def order_management(request):
    if session_check(request):
        order = Order.objects.exclude(
            payment__payment_method=None).order_by('-created_at')
        order_product = OrederProduct.objects.all()

        return render(request, 'admin/order_management.html', {'order': order})
    return redirect('admin_login')


def edit_order(request, id):
    order = Order.objects.filter(id=id)
    order.delete()
    return redirect('order_management')


def shipping_status(request, id):
    order = Order.objects.filter(id=id)
    if request.method == 'POST':
        shipping_status = request.POST['shipping_status']
        for ord in order:
            ord.shipping_status = shipping_status
            ord.save()

        return redirect('order_management')


def view_orders(request, id):
    if session_check(request):
        orde = OrederProduct.objects.filter(order_id=id)
        for ord in orde:
            print(ord.product.product_name)

        context = {
            'order': orde
        }
        return render(request, 'admin/orders.html', context)
    return redirect('admin_login')
# end Order management-----------------------------------------------------


# category management-----------------------------------------------------
def category_management(request):
    if session_check(request):
        cat = Category.objects.all()
        return render(request, 'admin/category_management.html', {'cat': cat})
    return redirect('admin_login')


def add_category(request):
    if session_check(request):
        print('here')
        if request.method == "POST":
            print('there')
            categ = request.POST['category_name']
            slug = request.POST['slugs']
            cat = Category(category_name=categ, slug=slug)

            cat.save()
            return redirect('category_management')

        return render(request, 'admin/category_management.html')
    return redirect('admin_login')


def del_category(request, pk):
    cat = Category.objects.get(id=pk)
    cat.delete()
    return redirect('category_management')


def edit_category(request, pk):
    cat = Category.objects.get(id=pk)
    if request.method == 'POST':
        categ = request.POST['category_name']
        slug = request.POST['slugs']

        cat.category_name = categ
        cat.slug = slug
        cat.save()
        return redirect('category_management')
    return render(request, 'admin/add_category.html', {'categ': cat})


# end category management-----------------------------------------------------


# Search products------------------------------------------------------------------

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']

        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
        else:
            return render(request, 'user/store.html')
    context = {
        'product': products,
        'count': product_count
    }
    return render(request, 'user/store.html', context)


# Reports------------------------------------------------------------------------
def weekly_report(request):
    if request.method == 'POST':
        date_from = request.POST['from']
        date_upto = request.POST['upto']

        items = OrederProduct.objects.filter(
            created_at__gt=date_from, created_at__lt=date_upto).order_by('-created_at')
    else:
        items = OrederProduct.objects.filter(created_at__gt=datetime.datetime.today(
        )-datetime.timedelta(days=7)).order_by('-created_at')
    context = {
        'order': items,
    }
    return render(request, 'admin/weekly_report.html', context)


def monthly_report(request):
    if request.method == 'POST':
        date_from = request.POST['from']
        date_upto = request.POST['upto']

        items = OrederProduct.objects.filter(
            created_at__gt=date_from, created_at__lt=date_upto).order_by('-created_at')
    else:

        items = OrederProduct.objects.filter(created_at__gt=datetime.datetime.today(
        )-datetime.timedelta(days=30)).order_by('-created_at')
    context = {
        'order': items,
    }
    return render(request, 'admin/monthly_report.html', context)


def yearly_report(request):
    if request.method == 'POST':
        date_from = request.POST['from']
        date_upto = request.POST['upto']

        items = OrederProduct.objects.filter(
            created_at__gt=date_from, created_at__lt=date_upto).order_by('-created_at')
    else:
        items = OrederProduct.objects.filter(created_at__gt=datetime.datetime.today(
        )-datetime.timedelta(days=365)).order_by('-created_at')

    context = {
        'order': items,
    }
    return render(request, 'admin/yearly_report.html', context)


# offer Management--------------------------------------------------------------
def offer_management_prod(request):
    # products = Product.objects.all()
    prod = ProductOffer.objects.all().order_by('-id')
    # categ = CategoryOffer.objects.all()

    context = {
        'prodd': prod,
        # 'category':categ,
        # 'products':products,
    }
    return render(request, 'admin/offer_management_product.html', context)


def offer_management_view_products(request):
    products = Product.objects.all()

    context = {
        # 'prod':prod,
        # 'category':categ,
        'products': products,
    }
    return render(request, 'admin/offer_management_prod.html', context)


def offer_management_cat(request):
    prod = ProductOffer.objects.all()
    categ = CategoryOffer.objects.all()

    context = {
        # 'prod':prod,
        'category': categ,
    }
    return render(request, 'admin/offer_management_cat.html', context)


def add_product_offer(request, product_id):
    product = Product.objects.all()

    if request.method == 'POST':
        print('inside post')
        offer_name = request.POST['offer_name']
        off_percentage = request.POST['off_percentage']
        # prod = request.POST['product']
        valid_from = request.POST['valid_from']
        valid_upto = request.POST['valid_upto']

        prod_offer = ProductOffer(offer_name=offer_name, off_percentage=off_percentage,
                                  product_id=product_id, valid_from=valid_from, valid_upto=valid_upto, expired=False)

        prod_offer.save()

        product = Product.objects.filter(id=product_id)
        for pro in product:
            reduce = (pro.price/100)*int(off_percentage)
            pro.offer_price = pro.price - reduce
            pro.save(update_fields=['offer_price'])
            print(pro.offer_price)
        return redirect('offer_management_prod')

    context = {

        'product': product,
    }
    return render(request, 'admin/add_offer.html', context)


def add_category_offer(request):
    category = Category.objects.all()

    if request.method == 'POST':
        print('inside post')
        offer_name = request.POST['offer_name']
        off_percentage = request.POST['off_percentage']
        cat = request.POST['category']
        valid_from = request.POST['valid_from']
        valid_upto = request.POST['valid_upto']
        print(cat)

        cat_offer = CategoryOffer(offer_name=offer_name, off_percentage=off_percentage,
                                  category_id=cat, valid_from=valid_from, valid_upto=valid_upto, expired=False)
        cat_offer.save()
        categ = Category.objects.get(id=cat)
        product = Product.objects.filter(category=categ.id)
        for pro in product:
            reduce = (pro.price/100)*int(off_percentage)
            pro.offer_price = pro.price-reduce
            pro.save(update_fields=['offer_price'])
            print(pro.offer_price)
            print(pro.product_name)

        return redirect('offer_management_cat')

    context = {

        'category': category
    }
    return render(request, 'admin/add_cat_offer.html', context)


def del_product_offer(request, product_id):

    product_offer = ProductOffer.objects.get(id=product_id)
    val = product_offer.product.id
    print(val)
    products = Product.objects.filter(id=val)
    for pro in products:
        pro.offer_price = None
        print(pro.offer_price)
    product_offer.delete()

    return redirect('offer_management_prod')


def del_category_offer(request, category_id):
    category_offer = CategoryOffer.objects.filter(id=category_id)
    categ = Category.objects.all()

    for cat in category_offer:
        products = Product.objects.filter(category_id=cat.category_id)
        for pro in products:
            pro.offer_price = None

    category_offer.delete()
    # print(products.offer_price)
    return redirect('offer_management_cat')


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(
                user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=review)
            form.save()
            return redirect(url)
        except ReviewRating.DoesNotExist:
            print('in here')
            form = ReviewForm(request.POST)
            if form.is_valid:
                data = ReviewRating()
                data.subject = request.POST['subject']
                data.rating = request.POST['rating']
                data.review = request.POST['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                return redirect(url)


def order_tracking(request, product_id):
    order = OrederProduct.objects.filter(
        user=request.user, product_id=product_id)

    context = {

        'order': order,

    }
    return render(request, 'user/order_tracking.html', context)


def coupon_management(request):

    coupon = Coupons.objects.all()

    context = {
        'coupons': coupon,
    }

    return render(request, 'admin/coupon_management.html', context)


def del_coupon(request, id):
    coup = Coupons.objects.get(id=id)
    coup.delete()
    return redirect('coupon_management')


def create_coupon(request):
    if request.method == 'POST':
        name = request.POST['coupon_name']
        off = request.POST['off_percentage']
        from_ = request.POST['valid_from']
        upto = request.POST['valid_upto']

        coup = Coupons(coupon_name=name, off_price=off,
                       valid_from=from_, valid_upto=upto)
        coup.save()
        return redirect('coupon_management')

    return render(request, 'admin/add_coupon.html')
