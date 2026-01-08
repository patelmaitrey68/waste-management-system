from typing import Any, Dict
from django.shortcuts import render,redirect
from django.views.generic import TemplateView,View
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from waste.models import user_Registration,waste_pickup,category,CollectionHistory,collector_Registration
# Create your views here.
class indexview(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name='collector/index.html'

class userview:
    @staticmethod
    @login_required(login_url='/login')
    def user_list(request):
        user=user_Registration.objects.all()
        return render(request,'collector/user_list.html',{'user':user})

class user_approve(LoginRequiredMixin, View):
    login_url = '/login'
    def dispatch(self, request, *args, **kwargs):
        id = request.GET.get('id')
        if not id:
            messages.error(request, 'No user id provided')
            return redirect('/collector')
        user = User.objects.get(pk=id)
        user.last_name='1'
        user.save()
        user = user_Registration.objects.filter(user__last_name='0',user__is_staff='0',user__is_active='1')
        return render(request,'collector/user_approvel.html',{'user':user,'message':" Account Approved"})

class user_reject(LoginRequiredMixin, View):
    login_url = '/login'
    def dispatch(self, request, *args, **kwargs):
        id = request.GET.get('id')
        if not id:
            messages.error(request, 'No user id provided')
            return redirect('/collector')
        user = User.objects.get(pk=id)
        user.last_name='1'
        user.is_active='0'
        user.save()
        return render(request,'collector/user_approvel.html',{'message':"Account Removed"})
    
class user_verify(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'collector/user_approvel.html'
    def get_context_data(self, **kwargs):
        context = super(user_verify,self).get_context_data(**kwargs)
        user = user_Registration.objects.filter(user__last_name='0',user__is_staff='0',user__is_active='1')
        context['user'] = user
        return context
    
class pickup_request(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name='collector/pickup_request.html'
    def get_context_data(self, **kwargs):
        context= super(pickup_request,self).get_context_data(**kwargs)
        pickup=waste_pickup.objects.filter(status='requested')
        context['pickup']=pickup
        return context

class waste_collect(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name='collector/waste_collect.html'
    def get_context_data(self, **kwargs):
       context= super(waste_collect,self).get_context_data(**kwargs)
       cat=category.objects.all()
       id=self.request.GET.get('id')
       obj = None
       if id:
           try:
               obj = waste_pickup.objects.get(id=id)
           except waste_pickup.DoesNotExist:
               messages.error(self.request, 'Pickup request not found')
       else:
           messages.error(self.request, 'No pickup id provided')
       context['pickup']=obj
       context['cat']=cat
       return context
    def post(self,request,*args,**kwargs):
        cat = request.POST.getlist('cat[]')
        qty = request.POST.getlist('qty[]')
        print("Category :",cat,"Qty: ",qty)
        pickupid = request.GET.get('id')
        if not pickupid:
            messages.error(request, 'No pickup id provided')
            return redirect('/collector')
        tpoint=0
        try:
            for cate, quantity in zip(cat, qty):  
                collection=CollectionHistory()
                obj = category.objects.get(name=cate)
                point=obj.point
                totalpoint=int(point)*float(quantity)
                wastepickup=waste_pickup.objects.get(id=pickupid)
                collection.pid=wastepickup
                collection.category=obj
                collection.weight=quantity
                collection.point=totalpoint
                tpoint=tpoint+totalpoint
                print("passed")
                collection.save()
            obj=waste_pickup.objects.get(id=pickupid)
            obj.pdate=timezone.now()
            obj.status='collected'
            try:
                collector = collector_Registration.objects.get(collector_id=self.request.user)
            except collector_Registration.DoesNotExist:
                messages.error(request, 'Collector account not found')
                return redirect('/collector')
            obj.collector=collector
            user=user_Registration.objects.get(id=obj.userid.id)            
            user.point=user.point+tpoint
            user.save()
            obj.save()
            message='SuccessFully Collected'
            messages.info(request,message)
            return redirect('/collector')
        except Exception as e:
            messages.info(request,e)
            return redirect('/collector')

class ViewCollection(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name="collector/collectionhis.html"
    def get_context_data(self, **kwargs):
        context= super(ViewCollection,self).get_context_data(**kwargs)
        # Prefer using authenticated user to find collector record
        context['total'] = 0
        context['col'] = []
        try:
            col = collector_Registration.objects.get(collector_id=self.request.user)
            collection = CollectionHistory.objects.filter(pid__collector=col.id)
            total_collected = CollectionHistory.objects.filter(pid__collector=col.id).aggregate(total_weight=Sum('weight'))
            context['total'] = total_collected['total_weight'] or 0
            context['col'] = collection
        except collector_Registration.DoesNotExist:
            messages.error(self.request, "Collector account not found. Please contact administrator.")
        return context
    
    
    def post(self, request, *args, **kwargs):
        strt_date = request.POST.get('strt_date')
        end_date = request.POST.get('end_date')
        try:
            col = collector_Registration.objects.get(collector_id=self.request.user)
            host = CollectionHistory.objects.filter(pid__collector=col.id,pid__pdate__gte=strt_date,pid__pdate__lte=end_date)
            total_collected = CollectionHistory.objects.filter(pid__collector=col.id,pid__pdate__gte=strt_date,pid__pdate__lte=end_date).aggregate(total_weight=Sum('weight'))
            total = total_collected['total_weight'] or 0
        except collector_Registration.DoesNotExist:
            messages.error(request, "Collector account not found. Please contact administrator.")
            host = []
            total = 0
        return render(request, 'collector/collectionhis.html', {'col':host,'total': total})
    