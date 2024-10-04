from django.contrib import admin
from Mywebsite.models import Quota
from Mywebsite.models import Profile
from .models import Quota, Enrollment
# Register your models here.

admin.site.register(Quota)
admin.site.register(Profile)
admin.site.register(Enrollment)  # จัดการโมเดล Enrollment