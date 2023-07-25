from urllib import request

from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from .forms import CustomerProfileForm, CustomerRegistrationForm
from .models import Cart, Customer, Product,Payment,OrderPlaced,Wishlist
import razorpay
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.
@login_required
def home(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Wishlist.objects.filter(user=request.user))
    return render(request,"app/home.html",locals())

@login_required
def about(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Wishlist.objects.filter(user=request.user))
    return render(request,"app/about.html",locals())

@login_required
def contact(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Wishlist.objects.filter(user=request.user))
    return render(request,"app/contact.html",locals())

@method_decorator(login_required,name='dispatch')
class CategoryView(View):
    def get(self, request, val):
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
            wishitem=len(Wishlist.objects.filter(user=request.user))
            totalitem=len(Cart.objects.filter(user=request.user))
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title').annotate(total=Count('title'))
        return render(request, "app/category.html", locals())

@method_decorator(login_required,name='dispatch')
class CategoryTitle(View):
    def get(self, request, val):
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
            wishitem=len(Wishlist.objects.filter(user=request.user))
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request, "app/category.html", locals())

@method_decorator(login_required,name='dispatch')
class ProductDetail(View):
     def get(self, request, pk):
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
            wishitem=len(Wishlist.objects.filter(user=request.user))
        product = Product.objects.get(pk=pk)
        wishlist=Wishlist.objects.filter(Q(product=product)& Q(user=request.user))
        return render(request, "app/productdetails.html", locals())

class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request, "app/customerregistration.html", locals())
    def post(self,request):
        form=CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Congratulation! User Registered Successfully")
        else:
            messages.warning(request,'Invalid Input Data')
        return render(request, "app/customerregistration.html", locals())

@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self,request):
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
            wishitem=len(Wishlist.objects.filter(user=request.user))
        form = CustomerProfileForm()
        return render(request,'app/profile.html',locals())
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user=request.user
            name= form.cleaned_data['name']
            locality= form.cleaned_data['locality']
            city= form.cleaned_data['city']
            mobile= form.cleaned_data['mobile']
            zipcode= form.cleaned_data['zipcode']

            reg= Customer(user=user,name=name,locality=locality,city=city,mobile=mobile,zipcode=zipcode)
            reg.save()
            messages.success(request, 'Congratulations! Profile Saved Successfully')
        else:
            message.warning(request, 'Invalid data')

        return render(request,'app/profile.html',locals())
        
@login_required
def address(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Wishlist.objects.filter(user=request.user))
    add = Customer.objects.filter(user=request.user)
    return render(request,'app/address.html',locals())

@method_decorator(login_required,name='dispatch')
class updateAddress(View):
    def get(self,request,pk):
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
            wishitem=len(Wishlist.objects.filter(user=request.user))
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request,'app/updateAddress.html',locals())
        
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add=Customer.objects.get(pk=pk)
            add.name= form.cleaned_data['name']
            add.locality= form.cleaned_data['locality']
            add.city= form.cleaned_data['city']
            add.mobile= form.cleaned_data['mobile']
            add.zipcode= form.cleaned_data['zipcode']
            add.save()
            messages.success(request, 'Congratulations! Profile Saved Successfully')
        else:
            message.warning(request, 'Invalid data')
        return redirect('address')

@login_required
def add_to_cart(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Wishlist.objects.filter(user=request.user))
    user = request.user
    product_id=request.GET.get('prod_id')
    product=Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect("/cart")        

@login_required
def show_cart(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Wishlist.objects.filter(user=request.user))
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount =0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 40
    return render(request, 'app/addtocart.html',locals())

@method_decorator(login_required,name='dispatch')
class checkout(View):
    def get(self,request):
        totalitem=0
        wishitem=0
        if request.user.is_authenticated:
            totalitem=len(Cart.objects.filter(user=request.user))
            wishitem=len(Wishlist.objects.filter(user=request.user))
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount=0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount=famount+value
        totalamount=famount+40
        razoramount=int(totalamount*100)
        client=razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
        data={"amount":razoramount,'currency':'INR','receipt':'order_rcptid_12'}
        payment_response = client.order.create(data=data)
        print(payment_response)
        # {'id': 'order_MFVvgQ4BlyOMoF', 'entity': 'order', 'amount': 8500, 'amount_paid': 0, 'amount_due': 8500, 'currency': 'INR', 'receipt': 'order_rcptid_12', 'offer_id': None, 'status': 'created', 'attempts': 0, 'notes': [], 'created_at': 1689737852}
        order_id=payment_response['id']
        order_status=payment_response['status']
        if order_status=='created':
            payment = Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status=order_status
            )
            payment.save()
        return render(request,'app/checkout.html',locals())

@login_required
def payment_done(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Wishlist.objects.filter(user=request.user))
    order_id=request.GET.get("order_id")
    payment_id=request.GET.get("payment_id")
    cust_id=request.GET.get('cust_id')
    user=request.user
    # to update payment status and payment id
    customer=Customer.objects.get(id=cust_id)
    payment=Payment.objects.get(razorpay_order_id=order_id)
    payment.paid=True
    payment.razorpay_payment_id=payment_id
    payment.save()
    # to save order details
    cart=Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity,payment=payment).save()
        c.delete()
    return redirect('orders')

@login_required
def orders(request):
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Wishlist.objects.filter(user=request.user))
    order_placed=OrderPlaced.objects.filter(user=request.user)
    return render(request,'app/orders.html',locals())

def plus_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        print(prod_id)
        c=Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.quantity+=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount,
        }
        return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.quantity-=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount,
        }
        return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.delete()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'amount':amount,
            'totalamount':totalamount,
        }
        return JsonResponse(data)

def plus_wishlist(request):
    if request.method=="GET":
        prod_id=request.GET['prod_id']
        product=Product.objects.get(id=prod_id)
        user=request.user
        Wishlist(user=user,product=product).save()
        data={
            'message':'Wishlist Added Successfully'
        }
        return JsonResponse(data)

def minus_wishlist(request):
    if request.method=="GET":
        prod_id=request.GET['prod_id']
        product=Product.objects.get(id=prod_id)
        user=request.user
        Wishlist.objects.filter(user=user,product=product).delete()
        data={
            'message':'Wishlist Removed Successfully'
        }
        return JsonResponse(data)

@login_required
def search(request):
    query=request.GET['search']
    totalitem=0
    wishitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
        wishitem=len(Wishlist.objects.filter(user=request.user))
    product=Product.objects.filter(Q(title__icontains=query))
    return render(request,'app/search.html',locals())




    

