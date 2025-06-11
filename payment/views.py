from django.shortcuts import render, redirect, get_object_or_404
from cart.cart import Cart
from payment.forms import ShippingForm, paymentForm
from payment.models import shippingAddress,Order,OrderItem
from django.contrib import messages
from django.contrib.auth.models import User
from store.models import Product,Profile
import datetime


def orders(request,pk):
    if request.user.is_authenticated and request.user.is_superuser:
        order = Order.objects.get(id=pk)
        items = OrderItem.objects.filter(order=pk)
        if request.POST:
            status = request.POST['shipping_status']
            if status == "true":
                order = Order.objects.filter(id=pk)
                now = datetime.datetime.now()
                order.update(shipped = True, date_shipped = now)
            else:
                order = Order.objects.filter(id=pk)
                order.update(shipped = False)
            messages.success(request,"Shipping Status Updated")
            return redirect('home')
        
            
        
        
        
        
        return render (request, 'payment/orders.html',{"order":order,"items":items})

    else:
        messages.error(request, 'Access denied')
        return redirect('home')



def not_shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=False)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			order = Order.objects.filter(id=num)
			now = datetime.datetime.now()
			order.update(shipped=True, date_shipped=now)
			messages.success(request, "Shipping Status Updated")
			return redirect('home')

		return render(request, "payment/not_shipped_dash.html", {"orders":orders})
	else:
		messages.success(request, "Access Denied")
		return redirect('home')

def shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=True)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			order = Order.objects.filter(id=num)
			now = datetime.datetime.now()
			order.update(shipped=False)
			messages.success(request, "Shipping Status Updated")
			return redirect('home')


		return render(request, "payment/shipped_dash.html", {"orders":orders})
	else:
		messages.success(request, "Access Denied")
		return redirect('home')


def payment_sucess(request):
    return render(request, 'payment/payment_sucess.html', {})
def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_products()
    quantities = cart.get_quantities()
    totals = cart.cart_total()

    if request.user.is_authenticated:
        shipping_user, created = shippingAddress.objects.get_or_create(user=request.user)

        # If it's a POST request, bind form to POST data
        if request.method == 'POST':
            shipping_form = ShippingForm(request.POST, instance=shipping_user)
            if shipping_form.is_valid():
                shipping_form.save()
                # Optionally redirect to billing or confirmation page
                # return redirect('billing')
        else:
            # GET request — show saved data
            shipping_form = ShippingForm(instance=shipping_user)

    else:
        if request.method == 'POST':
            shipping_form = ShippingForm(request.POST)
        else:
            shipping_form = ShippingForm()

    return render(request, 'payment/checkout.html', {
        'cart_products': cart_products,
        'quantities': quantities,
        'totals': totals,
        'shipping_form': shipping_form
    })

def billing_info(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            cart = Cart(request)
            cart_products = cart.get_products()
            quantities = cart.get_quantities()
            totals = cart.cart_total()

            my_shipping = request.POST.dict()
            request.session['my_shipping'] = my_shipping
            print("Shipping info saved in session:", my_shipping)

            shipping_form = shippingAddress.objects.filter(user=request.user).last()
            billing_form = paymentForm()
            return render(request, 'payment/billing_info.html', {
                'cart_products': cart_products,
                'quantities': quantities,
                'totals': totals,
                'shipping_info': shipping_form,
                'billing_form': billing_form
            })
        else:
            messages.error(request, 'Access denied: must use POST to access billing')
            return redirect('checkout')
    else:
        messages.error(request, "Access denied\n"
                       "To proceed you must login to your existing account, else register a new one")
        return redirect('profile')

    
def process_order(request):
    if request.method == 'POST':
        cart = Cart(request)
        cart_products = cart.get_products()
        quantities = cart.get_quantities()
        totals = cart.cart_total()           
        payment_form = paymentForm(request.POST)

        # Get shipping data from session
        my_shipping = request.session.get('my_shipping')

        if not my_shipping:
            messages.error(request, "Shipping information not found in session.")
            return redirect('checkout')  # Or another fallback

        # Build shipping_address before using it
        shipping_address = "\n".join([
            my_shipping.get('shipping_address1', ''),
            my_shipping.get('shipping_address2', ''),
            my_shipping.get('shipping_city', ''),
            my_shipping.get('shipping_state', ''),
            my_shipping.get('shipping_zipcode', ''),
            my_shipping.get('shipping_country', ''),
        ])

        name = my_shipping.get('shipping_name', '')
        email = my_shipping.get('shipping_email', '')
        amount_paid = totals

        if request.user.is_authenticated:
            user = request.user
            
            # Now use shipping_address here safely
            create_order = Order(
                user=user,
                name=name,
                email=email,
                shipping_address=shipping_address,
                amount_paid=amount_paid
            )
            create_order.save()
            
            order_id = create_order.pk
            for product in cart_products:
                product_id = product.id
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                    
                    
                for key, value in quantities.items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        create_order_item.save()
            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]
            current_user = Profile.objects.filter(user__id = request.user.id)
            current_user.update(old_cart="")
                
            
            
            
            
            messages.success(request,"Order placed")

            if payment_form.is_valid():
                # Process payment here if needed
                return redirect('payment_sucess')
            else:
                messages.error(request, "Invalid payment data.")
                return redirect('billing_info')

        else:
            messages.error(request,'Access denied, you need to be logged in.')
            return redirect('register')

    else:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    
    
