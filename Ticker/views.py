from django.shortcuts import render
from store.models import Product


def home(request):
    product = Product.objects.filter(is_available= True)
    context = {
        "product": product
        }
    return render(request, 'user/home.html', context)