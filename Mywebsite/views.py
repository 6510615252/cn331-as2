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
                # สร้างโปรไฟล์ใหม่
                Profile.objects.create(user=user)  # สร้างโปรไฟล์ให้กับผู้ใช้ใหม่
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
        subject_id = request.POST.get('subject_id')  # รับ ID ของวิชาจากฟอร์ม
        quota = Quota.objects.filter(id=subject_id).first()  # ดึงข้อมูล Quota ที่เลือก (จะเป็น None ถ้าไม่เจอ)

        if quota:  # ตรวจสอบว่ามี Quota หรือไม่
            if quota.Slot > 0:  # ตรวจสอบว่ามี Slot เหลืออยู่หรือไม่
                # บันทึกข้อมูลการลงทะเบียน
                Enrollment.objects.create(user=request.user, quota=quota)
                
                # ลดจำนวน Slot ลง 1
                quota.Slot -= 1
                
                # ถ้า Slot เหลือ 0 ให้เปลี่ยนสถานะเป็น Unavailable
                if quota.Slot == 0:
                    quota.Status = 'Unavailable'
                else: quota.Status = 'Available'
                
                quota.save()  # บันทึกการเปลี่ยนแปลง Slot และ Status ลงฐานข้อมูล
                messages.success(request, "ลงทะเบียนเรียบร้อยแล้ว")
            else:
                messages.error(request, "ไม่มี Slot ให้ลงทะเบียนแล้ว")  # หากไม่มี Slot
        else:
            messages.error(request, "เกิดข้อผิดพลาดในการลงทะเบียน")

        return redirect('main')  # เปลี่ยนไปยังหน้าอื่นหลังจากบันทึกข้อมูลเสร็จ

    return redirect('main')  # ถ้าไม่ใช่ POST ก็กลับไปยังหน้าหลัก

def cancel_quota(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        quota = Quota.objects.filter(id=subject_id).first()

        if quota:
            # ค้นหา Enrollment ที่ตรงกับผู้ใช้และ Quota
            enrollment = Enrollment.objects.filter(user=request.user, quota=quota).first()
            if enrollment:
                # ตรวจสอบว่าสถานะเป็น 'Pending' เท่านั้น
                if enrollment.approve == 'Pending':
                    enrollment.delete()  # ลบ Enrollment
                    quota.Slot += 1  # เพิ่ม Slot
                    quota.save()  # บันทึกการเปลี่ยนแปลง Slot
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
