from django.shortcuts import render, get_object_or_404, redirect
from .cart import Cart
from store.models import Product
from django.http import JsonResponse, HttpResponse
from django.contrib import messages

def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_products()
    quantities = cart.get_quantities()
    
    
    for product in cart_products:
        product.qty = quantities[str(product.id)]
    
    totals = cart.cart_total()
    return render(request, 'cart_summary.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals})

def cart_add(request):
    cart = Cart(request)
    
    if request.POST.get('action') == 'post':
        product_id = request.POST.get('product_id')
        if product_id is None:
            return HttpResponse("Missing product_id", status=400)
        product_id= int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))


        product= get_object_or_404(Product, id=product_id)
        
        
        cart.add(product=product, quantity=product_qty)
        
        cart_quantity = cart.__len__()
        
        
        
        response = JsonResponse({'qty' : cart_quantity})
        messages.success(request, 'Product added to cart successfully.')
        
        return response

        

def delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        cart.delete(product=product_id)
        response = JsonResponse({'product': product_id})
        messages.success(request, 'Product removed from cart successfully.')
        return response
    


def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        cart.update(product=product_id, quantity=product_qty)
        response = JsonResponse({'qty': product_qty})
        messages.success(request, 'Cart updated successfully.')
        return response

