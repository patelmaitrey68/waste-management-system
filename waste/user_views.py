from typing import Any, Dict
from django.shortcuts import render,redirect,HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from waste.models import waste_pickup,user_Registration,CollectionHistory,products,Purchase,OrderUpdates,Comaplaints,locations,stock_his
from django.contrib.auth.models import User
from django.contrib import messages


# Create your views here.
class indexview(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name='user/index.html'
    
    def dispatch(self, request, *args, **kwargs):
        # prefer Django authentication; fall back to legacy session key
        if not request.user.is_authenticated:
            messages.error(request, "User session not found. Please login again.")
            return redirect('/login')

        try:
            user_Registration.objects.get(user_id=request.user.id)
        except user_Registration.DoesNotExist:
            messages.error(request, "User account not found. Please complete registration.")
            return redirect('/login')
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(indexview,self).get_context_data(**kwargs)
        user = user_Registration.objects.get(user_id=self.request.user.id)
        context['user'] = user
        context['product'] = products.objects.all()
        return context
      
class pickup_request(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name='user/pickup_req.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = user_Registration.objects.get(user_id=self.request.user.id)
        context['user'] = user
        return context

    def post(self, request, *args, **kwargs):
        try:
            user_id = request.POST.get('user_id')
            user = user_Registration.objects.get(user_id=user_id) if user_id else user_Registration.objects.get(user=request.user)
            print(user)
            obj = waste_pickup()
            if  waste_pickup.objects.filter(userid=user.id,status='requested').exists():
                raise Exception
            obj.userid=user
            obj.save()
            message = 'Requested for pick up'
            messages.info(request, message)
            return redirect('/user')
        
        except Exception:
            message = "Unable to process request"
            messages.info(request, message)
            return redirect('/user')


class view_profile(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'user/view_profile.html'
    def get_context_data(self, **kwargs):
        context = super(view_profile,self).get_context_data(**kwargs)
        app_user = user_Registration.objects.filter(user_id=self.request.user.id)

        context['app_user'] = app_user
        return context

class edit_profile_view(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'user/edit_profile_view.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_user = user_Registration.objects.filter(user_id=self.request.user.id).first()

        context['app_user'] = app_user
        return context
    
    def post(self, request, *args, **kwargs):
        id = request.user.id
        name = request.POST['name']
        email = request.POST['email']
        mobile = request.POST['mobile']
        address = request.POST['address']
        pincode = request.POST['pincode']
        
        us = User.objects.get(pk=id)
        usr = user_Registration.objects.get(user_id=id)
        us.first_name = name
        us.email = email
        us.save()
        usr.name = name
        usr.email = email
        usr.address = address
        usr.mobile = mobile
        usr.pincode = pincode
    
        usr.save()
        message = 'Profile Updated'
        messages.success(request, message)
        return redirect('/user')

class history(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name='user/history.html'
    def get_context_data(self, **kwargs):
        context= super(history,self).get_context_data(**kwargs)
        user=user_Registration.objects.get(user_id=self.request.user.id)
        pickups=waste_pickup.objects.filter(userid=user.id)
        pickup_data=dict()
        for pickup in pickups:
            tpoint = CollectionHistory.objects.filter(pid=pickup.id).aggregate(tpoint=Sum('point'))['tpoint']
            pickup.tpoint = tpoint
            pickup_data[pickup.id] = tpoint
        print(pickup_data)
        context['data'] = pickup_data
        context['his']=pickups
        return context

class full_history(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name='user/fullhistory.html'
    def get_context_data(self, **kwargs):
        context= super(full_history,self).get_context_data(**kwargs)
        user=user_Registration.objects.get(user_id=self.request.user.id)
        
        if 'id' in self.request.GET and self.request.GET['id']:
            obj=CollectionHistory.objects.filter(pid=self.request.GET['id'])
            context['col']=obj
            return context
        
        pickups=CollectionHistory.objects.filter(pid__userid=user.id) 
        context['col']=pickups
        return context

class shop(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name='user/Shop.html'
    
    def get_context_data(self, **kwargs):
        context = super(shop,self).get_context_data(**kwargs)
        products_list = products.objects.filter(status=1)
        context['products'] = products_list
        return context
    
class view_product(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name='product.html'
    def get_context_data(self,**kwargs):
        context=super(view_product,self).get_context_data(**kwargs)
        pid=self.request.GET.get('id')
        pd=products.objects.get(id=pid)
        uid=User.objects.get(id=self.request.user.id)
        print(uid.last_name)
        context['uid']=uid
        #print("UserId :",uid)
        user=user_Registration.objects.get(user_id=uid)                                                                        
        context['user']=user
        
        context['pd']=pd
        return context
    
class checkout(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name='user/checkout.html'
    def get(self, request, *args, **kwargs):
        # basic validation of required GET params before rendering
        if not request.user.is_authenticated:
            messages.error(request, "Please login to continue")
            return redirect('/login')

        pid = request.GET.get('id')
        if not pid:
            messages.error(request, "No product specified for checkout")
            return redirect('/Shop')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(checkout, self).get_context_data(**kwargs)
        user = user_Registration.objects.get(user_id=self.request.user.id)

        pid = self.request.GET.get('id')
        pd = products.objects.get(id=pid)

        context['user'] = user
        context['pd'] = pd

        # determine operation mode: redeem or buy
        red = self.request.GET.get('red', 'f')
        if red == 't':
            opt = 'redeem'
            context['opt'] = opt
        else:
            opt = 'buy'
            # default quantity to 1 if not provided
            try:
                qty = int(self.request.GET.get('quantity', 1))
            except (ValueError, TypeError):
                qty = 1
            context['qty'] = qty
            total = int(qty) * pd.rate
            context['total'] = total
            context['opt'] = opt

        return context
    def post(self,request,*args,**kwargs):
        pur=Purchase()
        product=products.objects.get(id=self.request.GET['id'])
        stk=stock_his.objects.get(product=product.id)
        user=user_Registration.objects.get(user_id=self.request.session.get('id'))
        pur.user=user
        check_box=request.POST.get('check')
        if check_box=='on':
            pur.address=user.address
            pur.mobile=user.mobile
            pur.pincode=user.pincode
        else:
            pur.address=request.POST['add1']+" "+request.POST['add2']
            pur.mobile=request.POST['number']
            pur.pincode=request.POST['zip']
        pur.product=product   
        if 'redeem' in request.POST:
            user.point=user.point-product.point
            pur.type=pur.REDEEM
            pur.total=product.point
            stk.stock-=1
        else:
            qty=int(request.POST['qty'])
            pur.quantity=qty
            pur.type=pur.PURCHASE
            pur.total=product.rate*qty
            stk.stock-=qty
            print(product.rate*qty)
        pur.save()
        user.save()
        stk.save()
        message = 'Order Placed Successfully'
        messages.success(request, message)
        return redirect('/user')

class OrderHis(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name='user/orderhis.html'
    def get_context_data(self, **kwargs):
        user=user_Registration.objects.get(user_id=self.request.session.get('id'))
        context=super(OrderHis,self).get_context_data(**kwargs)
        order=Purchase.objects.filter(user=user.id)
        context['order']=order
        return context
    
class OrderUpdate(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name='user/orderupdates.html'
    def get_context_data(self, **kwargs):
        context=super(OrderUpdate,self).get_context_data(**kwargs)
        orderid=self.request.GET['id']
        update=OrderUpdates.objects.filter(order=orderid)
        context['update']=update
        return context
    
class ComplaintRegister(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = "user/registercomplaint.html"
    
    def post(self, request, *args, **kwargs):
        try:
            # Get the user ID from session
            user_id = request.session.get('id')
            if not user_id:
                messages.error(request, "Please login to register a complaint")
                return redirect('/login')

            # Get or create user registration
            try:
                user = user_Registration.objects.get(user_id=user_id)
            except user_Registration.DoesNotExist:
                messages.error(request, "User profile not found. Please complete your registration")
                return redirect('/user/profile')

            # Create the complaint
            complaint = Comaplaints()
            complaint.user = user
            complaint.subject = request.POST.get('subject')
            complaint.complaint = request.POST.get('complaint')
            complaint.save()

            messages.success(request, "Complaint registered successfully")
            return redirect('/user')

        except Exception as e:
            messages.error(request, f"Error registering complaint: {str(e)}")
            return render(request, self.template_name)

    def get(self, request, *args, **kwargs):
        # Add this to show the user's information in the form if needed
        context = self.get_context_data(**kwargs)
        user_id = request.session.get('id')
        if user_id:
            try:
                user = user_Registration.objects.get(user_id=user_id)
                context['user'] = user
            except user_Registration.DoesNotExist:
                messages.warning(request, "Please complete your profile first")
        return render(request, self.template_name, context)

class complaint_Status(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name="user/complaintstatus.html"
    def get_context_data(self, **kwargs):
        context=super(complaint_Status,self).get_context_data(**kwargs)
        user=self.request.session.get('id')
        uid=user_Registration.objects.get(user_id=user)
        comp=Comaplaints.objects.filter(user=uid)
        context['update']=comp
        return context

class Bill(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name="user/bill.html"
    def get_context_data(self, **kwargs):
        context=super(Bill,self).get_context_data(**kwargs)
        id=self.request.GET['id']
        pur=Purchase.objects.get(id=id)
        context['pur']=pur
        return context
    
class JoinUs(TemplateView):
    template_name="user/joinus.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        userid = self.request.session.get('id')
        user = user_Registration.objects.get(user_id=userid)
        if locations.objects.filter(pincode=user.pincode).exists():
            context['check']=True
        else:
            context['check']=False
        
        context['user'] = user
        print(context['check'])
        return context
    def post(self,request):
        user=User.objects.get(id=self.request.session.get("id"))
        user.last_name='0'
        user.save()
        message = 'Wait for verification'
        messages.success(request, message)
        return redirect('/user')