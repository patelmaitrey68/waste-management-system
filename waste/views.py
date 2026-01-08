from typing import Any, Dict
from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.contrib.auth.models import auth,User 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from django.contrib.auth import login
from django.http import JsonResponse
from waste.models import user_Registration,userType,products,locations, Feedback, collector_Registration
from django.contrib import messages
from django.contrib.auth.decorators import login_required

class indexview(TemplateView):
    template_name="home.html"
    def get_context_data(self, **kwargs):
        context=super(indexview,self).get_context_data(**kwargs)
        context['product']=products.objects.all()
        return context
    
# Remove the duplicate imports and clean up the login_view class
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views import View
from waste.models import user_Registration, collector_Registration

class login_view(View):
    template_name = "login.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        usertype = request.POST['usertype']
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            if usertype == 'user':
                try:
                    user_reg = user_Registration.objects.get(user=user)
                    request.session['uid'] = user.id
                    return redirect('/user/')
                except:
                    return render(request, self.template_name, {'message': 'Invalid user type selection'})
            
            elif usertype == 'collector':
                try:
                    collector = collector_Registration.objects.get(collector_id=user)
                    request.session['cid'] = user.id
                    return redirect('/collector/')
                except:
                    return render(request, self.template_name, {'message': 'Invalid user type selection'})
            
            elif usertype == 'admin':
                if user.is_superuser:
                    return redirect('/admin/')
                else:
                    return render(request, self.template_name, {'message': 'Invalid user type selection'})
            else:
                return render(request, self.template_name, {'message': 'Please select a valid user type'})
        else:
            return render(request, self.template_name, {'message': 'Invalid login credentials'})


def logout_view(request):
    """Log the user out and clear session keys used by the app."""
    logout(request)
    # Clear any custom session keys we set
    for k in ('uid', 'cid'):
        if k in request.session:
            try:
                del request.session[k]
            except KeyError:
                pass
    messages.info(request, 'You are now logged out.')
    return redirect('/')

class userRegistration(View):
    def get(self, request):
        return render(request, 'register.html')
    
    def post(self, request):
        try:
            name = request.POST.get('name', '')  # Using get() with default value
            email = request.POST.get('email', '')
            phone = request.POST.get('phone', '')
            address = request.POST.get('address', '')
            pincode = request.POST.get('pincode', '')
            password = request.POST.get('password', '')
            
            # Check if email already exists
            if User.objects.filter(username=email).exists():
                messages.error(request, "Email already registered")
                return render(request, 'register.html')
            
            # Create User
            user = User.objects.create_user(username=email, password=password)
            
            # Create UserRegistration
            user_reg = user_Registration()
            user_reg.user = user
            user_reg.name = name
            user_reg.phone = phone
            user_reg.address = address
            user_reg.pincode = pincode
            user_reg.save()
            
            messages.success(request, "Registration successful! Please login.")
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return render(request, 'register.html')

class shop(TemplateView):
    template_name='shop-guest.html'
    def get_context_data(self, **kwargs):
        context=super(shop,self).get_context_data(**kwargs)
        prod=products.objects.filter(status='1')
        context['prod']=prod
        return context
    
class view_product(TemplateView):
    template_name='product-guest.html'
    def get_context_data(self,**kwargs):
        context=super(view_product,self).get_context_data(**kwargs)
        pid=self.request.GET['id']
        pd=products.objects.get(id=pid)
        uid=self.request.session.get('id')
        #print("UserId :",uid)
        user=user_Registration.objects.get(user_id=uid)                                                                        
        context['user']=user
        context['pd']=pd
        return context
    
def check_pincode_view(request):
    if request.method == 'GET':
        pincode = request.GET.get('pincode', '')
        exists = locations.objects.filter(pincode=pincode).exists()
        return JsonResponse({'exists': exists})
    
class view_product(TemplateView):
    template_name='product.html'
    def get_context_data(self,**kwargs):
        context=super(view_product,self).get_context_data(**kwargs)
        pid=self.request.GET['id']
        pd=products.objects.get(id=pid)
        context['pd']=pd
        return context
        
from django.views import View
class CheckPincodeView(View):
    def get(self, request):
        pincode = request.GET.get('pincode')
        
        # Replace this with your actual pincode validation logic
        valid_pincodes = locations.objects.all()
        for i in valid_pincodes:
            if pincode == i.pincode:
                message = 'Valid pincode'
                print( i.pincode)
                return JsonResponse({'message': message})
            else:
                print( i.pincode)
                message = 'Invalid pincode'
        
        return JsonResponse({'message': message})
class Check(TemplateView):
    template_name="chech.html"

class FeedbackView(View):
    template_name = 'feedback.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        Feedback.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        messages.success(request, 'Thank you for your feedback!')
        return redirect('feedback')

def check_collector_registration(request):
    total_collectors = collector_Registration.objects.all().count()
    last_collector = collector_Registration.objects.last()
    
    if last_collector:
        last_collector_data = {
            'name': last_collector.name,
            'phone': last_collector.phone,
            'status': last_collector.status
        }
    else:
        last_collector_data = None
        
    return JsonResponse({
        'total_collectors': total_collectors,
        'last_collector': last_collector_data
    })
class collectorRegistration(View):
    def get(self, request):
        return render(request, 'collector/collector_register.html')
    
    def post(self, request):
        try:
            # Get form data
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            pincode = request.POST.get('pincode')
            password = request.POST.get('password')
            
            # Check if email already exists
            if User.objects.filter(username=email).exists():
                messages.error(request, "Email already registered")
                return render(request, 'collector/collector_register.html')
            
            # Create User
            user = User.objects.create_user(username=email, password=password)
            
            # Create Collector Registration
            collector = collector_Registration()
            collector.collector_id = user
            collector.name = name
            collector.phone = phone
            collector.address = address
            collector.pincode = pincode
            collector.status = 0  # Pending approval
            collector.save()
            
            messages.success(request, "Registration successful! Please wait for admin approval.")
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return render(request, 'collector/collector_register.html')
