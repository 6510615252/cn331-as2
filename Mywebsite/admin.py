from django.contrib import admin
from Mywebsite.models import Quota
from Mywebsite.models import Profile
from .models import Quota, Enrollment
# Register your models here.

admin.site.register(Quota)
admin.site.register(Profile)

from django.contrib import admin
from .models import Enrollment

def approve_enrollment(modeladmin, request, queryset):
    queryset.update(approve='Approved')

def reject_enrollment(modeladmin, request, queryset):
     for enrollment in queryset:
        enrollment.approve = 'Rejected'
        enrollment.quota.Slot += 1  # เพิ่ม Slot เมื่อปฏิเสธ
        enrollment.quota.save()  # บันทึกการเปลี่ยนแปลงใน Quota
        enrollment.save()  # บันทึกการเปลี่ยนแปลงใน Enrollment

approve_enrollment.short_description = "Approve selected enrollments"
reject_enrollment.short_description = "Reject selected enrollments"

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'quota', 'approve')
    list_filter = ('approve',)
    actions = [approve_enrollment, reject_enrollment]  # เพิ่ม action ที่สร้างขึ้น

admin.site.register(Enrollment, EnrollmentAdmin)