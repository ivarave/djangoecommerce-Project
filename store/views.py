from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django.db.models import Q
import json
from cart.cart import Cart
from payment.forms import ShippingForm
from payment.models import shippingAddress
from django.core.paginator import Paginator






def home(request):
    products = Product.objects.all()
    paginator = Paginator(products,4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'home.html', {'page_obj': page_obj})

def about(request):
    return render(request, 'about.html',{})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            current_user = Profile.objects.get(user__id=request.user.id)
            saved_cart = current_user.old_cart
            if saved_cart:
                converted_cart = json.loads(saved_cart.replace("'", '"'))
                cart = Cart(request)
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)
                    
            messages.success(request, 'You have been logged in successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')
        
    else:
        
        return render(request, 'login.html',{})
    
def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('profile')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'You have registered successfully. Continue to update your information')
            return redirect ('update_info')
        else:
            messages.success(request, 'There was a problem with your registration.')
            return render(request, 'register.html', {'form':form} )
        
    else:
        return render(request, 'register.html', { 'form' : form})
    
    
def profile(request):
    return render(request, 'profile.html')


def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product': product})


def category(request, foo):
	foo = foo.replace('-', ' ')
	try:
		category = Category.objects.get(name=foo)
		products = Product.objects.filter(category=category)
		return render(request, 'category.html', {'products':products, 'category':category})
	except:
		messages.success(request, ("That Category Doesn't Exist..."))
		return redirect('home')

    
    
def category_summary(request):
    category = Category.objects.all()
    paginator = Paginator(category,1000000000000000000)  
    page_number = request.GET.get('page')
    page_obj_categories = paginator.get_page(page_number)
    return render(request, 'category_summary.html', { 'page_obj_categories': page_obj_categories})


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()
            
            login(request, current_user)
            
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
        
        return render(request, 'update_user.html', {'user_form': user_form})
    else:
        messages.error(request, 'You need to be logged in to update your profile.')
        return redirect('login')
        
        
def update_info(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user=request.user)

        shipping_user, created = shippingAddress.objects.get_or_create(user=request.user)

        if request.method == 'POST':
            form = UserInfoForm(request.POST, instance=current_user)
            shipping_form = ShippingForm(request.POST, instance=shipping_user)

            form_valid = form.is_valid()
            shipping_valid = shipping_form.is_valid()

            if form_valid:
                form.save()
            else:
                messages.error(request, 'Please correct the errors in your profile form.')

            if shipping_valid:
                shipping_form.save()
                
            if not form_valid and not shipping_valid:
                messages.error(request, 'Please correct the errors in both forms.')


            if form_valid and shipping_valid:
                messages.success(request, 'Your profile and shipping information have been updated successfully.')
                return redirect('profile')

        else:
            form = UserInfoForm(instance=current_user)
            shipping_form = ShippingForm(instance=shipping_user)

        return render(request, 'update_info.html', {
            'form': form,
            'shipping_form': shipping_form
        })
    else:
        messages.error(request, 'You need to be logged in to update your profile info.')
        return redirect('login')

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = ChangePasswordForm(current_user,request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been updated successfully.')
                login(request, current_user)
                return redirect('profile')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
                

        else:
            form = ChangePasswordForm(user=current_user)
            return render(request, 'update_password.html', {'form': form})
    
    else:
        messages.error(request, 'You need to be logged in to change your password.')
        return redirect('home')
    
    
    
    
def search(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched) | Q(category__name__icontains=searched)).distinct()
        if not searched:
            messages.error(request, 'No products found matching your search.')
            return render(request, "search.html", {})
        else:
            messages.success(request, f'Found {searched.count()} products matching your search.')
            return render(request, "search.html", {'searched': searched})
        
    else:
        return render(request, "search.html", {})
    
        

