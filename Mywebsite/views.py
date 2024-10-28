from django.http import HttpResponse
from django.shortcuts import render, redirect
from Mywebsite.models import Quota
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import admin
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Quota, Enrollment
from django.shortcuts import render, get_object_or_404





# Create your views here.
def index(request):
    all_subject = Quota.objects.all()   
    registered_subjects = Enrollment.objects.filter(user=request.user).values_list('quota_id', flat=True)
    return render(request,"main.html",{"all_subject":all_subject,  'registered_subjects': registered_subjects})

def history(request):
    all_enrollment = Enrollment.objects.filter(user=request.user)
    return render(request, 'history.html', {"all_enrollment":all_enrollment})

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username = username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "login.html")

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        
        if password == confirm_password:
            try:
                user = User.objects.create_user(username=username, password=password)
               
                Profile.objects.create(user=user) 
                messages.success(request, "Registration successful. You can now log in.")
                return redirect('login')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Passwords do not match.")
    
    return render(request, "register.html")

@login_required
def register_quota(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id') 
        quota = Quota.objects.filter(id=subject_id).first()  

        if quota:  
            if quota.Slot > 0:  
              
                Enrollment.objects.create(user=request.user, quota=quota)
                
               
                quota.Slot -= 1
                
               
                if quota.Slot == 0:
                    quota.Status = 'Unavailable'
                else: quota.Status = 'Available'
                
                quota.save()  
                messages.success(request, "ลงทะเบียนเรียบร้อยแล้ว")
            else:
                messages.error(request, "ไม่มี Slot ให้ลงทะเบียนแล้ว")  
        else:
            messages.error(request, "เกิดข้อผิดพลาดในการลงทะเบียน")

        return redirect('main')  

    return redirect('main') 

def cancel_quota(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        quota = Quota.objects.filter(id=subject_id).first()

        if quota:
            
            enrollment = Enrollment.objects.filter(user=request.user, quota=quota).first()
            if enrollment:
                
                if enrollment.approve == 'Pending':
                    enrollment.delete() 
                    quota.Slot += 1 
                    quota.save() 
                    messages.success(request, 'ยกเลิกการลงทะเบียนแล้ว')
                elif enrollment.approve == 'Rejected':
                    enrollment.delete()
                    quota.save()
                    messages.success(request, 'ลบรายวิชาที่ถูกปฎิเสธแล้ว')
                else:
                    messages.error(request, 'ไม่สามารถยกเลิกได้ เนื่องจากสถานะไม่อนุญาต')
            else: 
                messages.error(request, 'ไม่พบการลงทะเบียนที่ต้องการยกเลิก')

            return redirect('history')
        messages.error(request, 'ไม่พบ Quota ที่ต้องการ')
        return redirect('history')
    
def subject_detail(request, subject_id):
    subject = get_object_or_404(Quota, id=subject_id)
    return render(request, 'subject_detail.html', {'subject': subject})
