from store.models import Product,Profile
from decimal import Decimal

class Cart:
    def __init__(self, request):
        self.session = request.session
        self.request = request
        
        cart = self.session.get('session_key')
        
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
            
        self.cart = cart

    def add(self, product, quantity ):
        product_id = str(product.id)
        product_qty = str(quantity)
        if product_id  in self.cart:
            pass
        else:
            self.cart[product_id] = int(product_qty)
        
        self.session.modified = True
        if self.request.user.is_authenticated:
            current_user  = Profile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("'", '"')
            current_user.update(old_cart=carty)
            
    def db_add(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)
        
        if product_id in self.cart:
            pass
        else:
            self.cart[product_id] = int(product_qty)
        
        self.session.modified = True
        if self.request.user.is_authenticated:
            current_user  = Profile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("'", '"')
            current_user.update(old_cart=carty)
        
    def __len__(self):
        return len(self.cart)
    
    def get_products (self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        return products
        
        
    def get_quantities(self):
        quantities = self.cart
        return quantities
    
    
    def update(self,product,quantity):
        product_id = str(product)
        product_qty = int(quantity)
        
        ourcart = self.cart
        ourcart[product_id] = product_qty
        self.session.modified = True
        
        if self.request.user.is_authenticated:
            current_user  = Profile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("'", '"')
            current_user.update(old_cart=carty)
        
        thing = self.cart
        return thing
    
    
    def delete(self,product):
        product_id = str(product)
        if product_id in self.cart:
            del self.cart[product_id]
        self.session.modified = True
        
        if self.request.user.is_authenticated:
            current_user  = Profile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("'", '"')
            current_user.update(old_cart=carty)
        
        
        
        
    def cart_total(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        quantities = self.cart
        total = 0
        for key, value in quantities.items():
            key = int(key)
            for product in products:
                if product.is_sale:
                    if product.id == key:
                        total = total + (Decimal (product.sale_price) * int(value))
                else:
                    if product.id == key:
                        total = total + (Decimal (product.price) * int(value))
        return total
    
    
    
    
        