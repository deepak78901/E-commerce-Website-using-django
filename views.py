from django.db.models import  Count
from urllib import request
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views import View
from.models import Product,Cart,Wishlist
from.forms import CustomerProfileForm,CustomerRegistrationForm
from django.contrib import messages
from .models import Customer,Payment,OrderPlaced
from django.http import JsonResponse
from django.db.models import Q 
from django.views.generic import TemplateView
import razorpay
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
@login_required
def index(request):
   totalitem=0
   if request.user.is_authenticated:
      totalitem=len(Cart.objects.filter(user=request.user))
   return render(request,'app/home.html')
@login_required
def about(request):
   totalitem=0
   if request.user.is_authenticated:
      totalitem=len(Cart.objects.filter(user=request.user))

   return render(request,'app/about.html')
@login_required
def contact(request):
   totalitem=0
   if request.user.is_authenticated:
      totalitem=len(Cart.objects.filter(user=request.user))
   return render(request,'app/contact.html')

@method_decorator(login_required,name='dispatch')
class categoryView(View):
   def get(self,request,val):
      totalitem=0
      if request.user.is_authenticated:
         totalitem=len(Cart.objects.filter(user=request.user))
      product=Product.objects.filter(category=val)
      title=Product.objects.filter(category=val)
      return render(request, 'app/category.html',locals())

@method_decorator(login_required,name='dispatch')   
class categoryTitle(View):
   def get(self,request,val):
      product=Product.objects.filter(Title=val)
      title=Product.objects.filter(category=product[0].category).values('title')
      totalitem=0
      if request.user.is_authenticated:
         totalitem=len(Cart.objects.filter(user=request.user))
      return render(request, 'app/category.html',locals())
   
@method_decorator(login_required,name='dispatch')   
class ProductDetail(View):
   def get(self,request,pk):
      product=Product.objects.get(pk=pk)
      wishlist=Wishlist.objects.filter(Q(product=product) & Q(user=request.user))
      totalitem=0
      if request.user.is_authenticated:
         totalitem=len(Cart.objects.filter(user=request.user))
      return render(request,"app/productdetail.html",locals())
   
@method_decorator(login_required,name='dispatch')
class CustomerRegistrationView(View):
   def get(self,request):
      form=CustomerRegistrationForm()
      totalitem=0
      if request.user.is_authenticated:
         totalitem=len(Cart.objects.filter(user=request.user))
      return render(request,"app/customerragistration.html",locals())
   def post(self,request):
      form=CustomerRegistrationForm(request.POST)
      if form.is_valid():
         form.save()
         messages.success(request,"Cogratulation! User Ragister Successfully")
      else:
         messages.warning(request,"Invalid Input Data")
      return render(request,"app/customerragistration.html",locals())

@method_decorator(login_required,name='dispatch')
class ProfileView(View):
   def get(self,request):
      form=CustomerProfileForm()
      totalitem=0
      if request.user.is_authenticated:
         totalitem=len(Cart.objects.filter(user=request.user))
      return render(request,'app/profile.html',locals())
   def post(self,request):
      return render(request,'app/profile.html',locals())
   def post(self,request):
      form=CustomerProfileForm(request.POST)
      if form.is_valid():
         user=request.user
         name=form.cleaned_data['name']
         locality=form.cleaned_data['locality']
         city=form.cleaned_data['city']
         mobile=form.cleaned_data['mobile']
         state=form.cleaned_data['state']
         zipcode=form.cleaned_data['zipcode']

         reg=Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
         reg.save()
         messages.success(request,"congratulation! profile save successfully")
      else:
         messages.warning(request,"Invalid Input Data")

      return render(request,'app/profile.html',locals())
@login_required
def address(request):
   add=Customer.objects.filter(user=request.user)
   totalitem=0
   if request.user.is_authenticated:
      totalitem=len(Cart.objects.filter(user=request.user))
   return render(request,'app/address.html',locals())

@method_decorator(login_required,name='dispatch')
class updateAddress(View):
   def get(self,request,pk):
      add=Customer.objects.get(pk=pk)
      form=CustomerProfileForm(instance=add)
      totalitem=0
      if request.user.is_authenticated:
         totalitem=len(Cart.objects.filter(user=request.user))
      return render(request,'app/updateAddress.html',locals())
   def post(self,request,pk):
      form=CustomerProfileForm(request.POST)
      if form.is_valid():
           add=Customer.objects.get(pk=pk)
           add.name=form.cleaned_data['name']
           add.locality=form.cleaned_data['locality']
           add.city=form.cleaned_data['city']
           add.mobile=form.cleaned_data['mobile']
           add.state=form.cleaned_data['state']
           add.zipcode=form.cleaned_data['zipcode']
           add.save()
           messages.success(request,"congratulationorifile update successfully")
      else:
         messages.warning(request,"invalid input data")
      return redirect("address")
def add_to_cart(request):
   user=request.user
   prod_id = request.GET.get('prod_id', '').strip('/')  # Remove trailing slashes
   if not prod_id.isdigit():
      return JsonResponse({'error': 'Invalid product ID'}, status=400)
   prod_id = int(prod_id)
   product=Product.objects.get(id=prod_id)
   Cart(user=user,product=product).save()
   return redirect("/cart")
@login_required 
def show_cart(request):
   user=request.user
   cart=Cart.objects.filter(user=user)
   amount=0
   for p in cart:
      value=p.quantity*p.product.discounted_price
      amount=amount+value
   totalamount=amount+40
   totalitem=0
   if request.user.is_authenticated:
      totalitem=len(Cart.objects.filter(user=request.user))
   return render(request,'app/addtocart.html',locals())

@method_decorator(login_required,name='dispatch')  
class CheckoutView(TemplateView):
   def get(self,request):
      totalitem=0
      if request.user.is_authenticated:
         totalitem=len(Cart.objects.filter(user=request.user))
      user=request.user
      add=Customer.objects.filter(user=user)
      cart_items=Cart.objects.filter(user=user)
      famount=0
      for p in cart_items:
         value=p.quantity * p.product.discounted_price
         famount=famount+value
      totalamount=famount+40
      razoramount= int(totalamount * 100)
      client=razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
      data={"amount":razoramount,"currency":'INR',"receipt":"order_rcptid_12"}
      payment_response=client.order.create(data=data)
      print(payment_response)
      #{'amount': 54100, 'amount_due': 54100, 'amount_paid': 0, 'attempts': 0, 'created_at': 1733652403, 'currency': 'INR', 'entity': 'order', 'id': 'order_PUdvyo1zBFsoNn', 'notes': [], 'offer_id': None, 'receipt': 'order_rcptid_12', 'status': 'created'}
      order_id=payment_response['id']
      order_status = payment_response['status']
      payment=Payment (
         user=user,
         amount=totalamount,
         razorpay_order_id=order_id,
         razorpay_payment_status=order_status
      )
      payment.save()
      return render(request,'app/checkout.html',locals())
   
@login_required
def payment_done(request):
   order_id=request.GET.get('order_id')
   payment_id=request.GET.get('payment_id')
   cust_id=request.GET.get('cust_id')
   user=request.user
   customer=Customer.objects.get(id=cust_id)
   payment=Payment.objects.get(razorpay_order_id=order_id)
   payment.paid=True
   payment.razorpay_payment_id=payment_id
   payment.save()
   cart=Cart.objects.filter(user=user)
   for c in cart:
      OrderPlaced(user=user,customer=c.customer,product=c.product,quantity=c.quantity,payment=payment).save()
      c.delete
   return redirect("orders")

@login_required
def orders(request):
   totalitem=0
   if request.user.is_authenticated:
      totalitem=len(Cart.objects.filter(user=request.user))
   order_placed=OrderPlaced.objects.filter(user=request.user)
   return render(request,'app/orders.html',locals())

@login_required
def plus_cart(request):


   if request.method=='GET':
      prod_id=request.GET['prod_id']
      c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
      c.quantity+=1
      c.save()
      user=request.user
      cart=Cart.objects.filter(user=user)
      amount=0
      for p in cart:
         value=p.quantity * p.product.discounted_price
         amount=amount+value
      totalamount=amount+40
      data= {
         'quantity':c.quantity,
         'amount':amount,
         'totalamount':totalamount,
      }
      return JsonResponse(data)
   
@login_required
def minus_cart(request):
   if request.method=='GET':
      prod_id=request.GET['prod_id']
      c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
      c.quantity-=1
      c.save()
      user=request.user
      cart=Cart.objects.filter(user=user)
      amount=0
      for p in cart:
         value=p.quantity * p.product.discounted_price
         amount=amount+value
      totalamount=amount+40
      data= {
         'quantity':c.quantity,
         'amount':amount,
         'totalamount':totalamount,
      }
      return JsonResponse(data)
   
@login_required
def remove_cart(request):
   if request.method=='GET':
      prod_id=request.GET['prod_id']
      c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
      c.delete()
      user=request.user
      cart=Cart.objects.filter(user=user)
      amount=0
      for p in cart:
         value=p.quantity * p.product.discounted_price
         amount=amount+value
      totalamount=amount+40
      data= {
         'quantity':c.quantity,
         'totalamount':totalamount,
      }
      return JsonResponse(data)
   
@login_required
def plus_wishlist(request):
   if request.method=='GET':
      prod_id=request.GET['prod_id']
      product=Product.objects.get(id=prod_id)
      user=request.user
      Wishlist(user=user,product=product).save()
      data={
         'message':'Wishlist Added Successfully',

      }
      return JsonResponse(data)
   
@login_required
def minus_wishlist(request):
   if request.method=='GET':
      prod_id=request.GET['prod_id']
      product=Product.objects.get(id=prod_id)
      user=request.user
      Wishlist(user=user,product=product).delete()
      data={
         'message':'Wishlist Remove Successfully',

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
   return render(request,"app/search.html",locals())

       