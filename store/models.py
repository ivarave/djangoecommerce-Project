from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save







class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(User, auto_now=True)
    phone = models.CharField(max_length=20, default="", blank=True, null=True)
    address1 = models.CharField(max_length=255, default="", blank=True, null=True)
    address2 = models.CharField(max_length=255, default="", blank=True, null=True)
    city = models.CharField(max_length=100, default="", blank=True, null=True)
    state = models.CharField(max_length=100, default="", blank=True, null=True)
    zip_code = models.CharField(max_length=20, default="", blank=True, null=True)
    country = models.CharField(max_length=100, default="", blank=True, null=True)
    old_cart = models.CharField(max_length=200, default="", blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
        
post_save.connect(create_profile, sender=User)
    
    


class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
    
    
    
class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=11)
    address = models.CharField(max_length=255)
    password = models.CharField(max_length=100)
    
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.CharField(max_length=100, default="", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,default =1)
    image = models.ImageField(upload_to='uploads/product/')
    
    is_sale = models.BooleanField(default=False)
    sale_price = models.CharField(max_length=100, default="0", blank=True, null=True)
    
    def __str__(self):
        return self.name
    

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=255, default="", blank=True, null=True)
    phone = models.CharField(max_length=11, default="", blank=True, null=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.product
    