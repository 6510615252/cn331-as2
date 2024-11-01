from django.test import TestCase
from django.contrib.auth.models import User
from .models import Quota, Profile, Enrollment
from django.urls import reverse


class MyViewTests(TestCase):

    def setUp(self):
        # สร้างผู้ใช้สำหรับการทดสอบ
        self.user = User.objects.create_user(username='testuser', password='password')
        # สร้าง Quota สำหรับผู้ใช้ทดสอบ
        self.quota = Quota.objects.create(Subject='Test Subject', Year=2024, Semester=1, Slot=1, Status='Available')

    def test_login_view_requires_login(self):
        """"ทดสอบว่าหน้าล็อกอินสามารถเข้าถึงได้หรือไม่"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")  # ตรวจสอบว่ามีข้อความ "Login" ในหน้าล็อกอินหรือไม่

    def test_successful_login(self):
        """ทดสอบการล็อกอินที่สำเร็จ"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password'
        })
        self.assertRedirects(response, reverse('main'))  # ตรวจสอบว่าหลังจากล็อกอินแล้วถูกเปลี่ยนเส้นทางไปยังหน้า 'main'

    def test_failed_login(self):
        """ทดสอบการล็อกอินที่ไม่สำเร็จ"""
        response = self.client.post(reverse('login'),{
            'username': 'wronguser',  #ชื่อผู้ใช้ไม่ถูกต้อง
            'password': 'wrongpassword' #รหัสผ่านไม่ถูกต้อง
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")

    def test_register_false(self):
        """ทดสอบการลงทะเบียนเมื่อข้อมูลไม่ถูกต้อง (รหัสผ่านไม่ตรงกัน)"""
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password': 'password',
            'confirm_password': 'not_matching_password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Passwords do not match.")  # ตรวจสอบว่ามีข้อความแจ้งเตือนเรื่องรหัสผ่านไม่ตรงกัน

    def test_successful_registration(self):
        """ทดสอบการลงทะเบียนที่สำเร็จ"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'newpassword',
            'confirm_password': 'newpassword'
        })
        self.assertRedirects(response, reverse('login'))  # ตรวจสอบว่าหลังจากลงทะเบียนถูกเปลี่ยนเส้นทางไปยังหน้า 'login'
        new_user = User.objects.get(username='newuser')  # ตรวจสอบว่าผู้ใช้ใหม่ถูกสร้างขึ้น
        self.assertIsNotNone(new_user)

    def test_failed_registration_duplicate_username(self):
        """"ทดสอบการลงทะเบียนที่ล้มเหลวเนื่องจากชื่อผู้ใช้ซ้ำ"""
        response = self.client.post(reverse('register'), {
            'username': 'testuser',  # ชื่อผู้ใช้นี้มีอยู่แล้ว
            'password': 'password',
            'confirm_password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "An error occurred")  # ตรวจสอบว่ามีข้อความแจ้งเตือนเกี่ยวกับข้อผิดพลาด

    def test_successful_register_quota(self):
        """ทดสอบการลงทะเบียน Quota ที่สำเร็จ"""
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('register_quota'), {'subject_id': self.quota.id})
        self.assertRedirects(response, reverse('main'))  # ตรวจสอบว่าหลังจากลงทะเบียน Quota แล้วถูกเปลี่ยนเส้นทางไปยังหน้า 'main'
        enrollment = Enrollment.objects.filter(user=self.user, quota=self.quota).first()  # ตรวจสอบว่ามีการลงทะเบียนเกิดขึ้น
        self.assertIsNotNone(enrollment)

class QuotaModelTest(TestCase):
    def setUp(self):
        # สร้าง Quota สำหรับการทดสอบ
        self.quota = Quota.objects.create(
            Subject="Mathematics",
            Year=2023,
            Semester=1,
            Slot=30,
            Status="Open"
        )

    def test_quota_creation(self):
        """"ทดสอบการสร้าง Quota"""
        self.assertTrue(isinstance(self.quota, Quota))  # ตรวจสอบว่า Quota ถูกสร้างขึ้นอย่างถูกต้อง
        self.assertEqual(self.quota.__str__(), "Mathematics 2023 1 30 Open")  # ตรวจสอบว่าค่าที่แสดงถูกต้อง

class ProfileModelTest(TestCase):

    def setUp(self):
        # สร้างผู้ใช้และโปรไฟล์สำหรับการทดสอบ
        self.user = User.objects.create_user(username="testuser", password="password")
        self.profile = Profile.objects.create(user=self.user)

    def test_profile_creation(self):
        """ทดสอบการสร้างโปรไฟล์"""
        self.assertTrue(isinstance(self.profile, Profile))  # ตรวจสอบว่าโปรไฟล์ถูกสร้างขึ้นอย่างถูกต้อง
        self.assertEqual(self.profile.__str__(), "testuser")  # ตรวจสอบว่าค่าที่แสดงถูกต้อง

class EnrollmentModelTest(TestCase):

    def setUp(self):
        # สร้างผู้ใช้, Quota, และการลงทะเบียนสำหรับการทดสอบ
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username='testuser', password='password')
        self.quota = Quota.objects.create(
            Subject="Mathematics",
            Year=2023,
            Semester=1,
            Slot=30,
            Status="Open"
        )
        self.enrollment = Enrollment.objects.create(user=self.user, quota=self.quota, approve="Pending")

    def test_enrollment_creation(self):
        """ทดสอบการสร้างการลงทะเบียน"""
        self.assertTrue(isinstance(self.enrollment, Enrollment))  # ตรวจสอบว่าการลงทะเบียนถูกสร้างขึ้นอย่างถูกต้อง
        self.assertEqual(self.enrollment.__str__(), "testuser enrolled in Mathematics")  # ตรวจสอบว่าค่าที่แสดงถูกต้อง
        self.assertEqual(self.enrollment.approve, "Pending")  # ตรวจสอบว่าสถานะการอนุมัติถูกต้อง
    
    def test_successful_cancel_quota(self):
        """ทดสอบการยกเลิกการลงทะเบียน Quota """
        # สร้างการลงทะเบียนสำหรับผู้ใช้
        Enrollment.objects.create(user=self.user, quota=self.quota, approve='Pending')

        response = self.client.post(reverse('cancel_quota'), {'subject_id': self.quota.id})
        self.assertRedirects(response, reverse('history'))  # ตรวจสอบว่าหลังจากยกเลิกถูกเปลี่ยนเส้นทางไปยังหน้า 'history'

        # ตรวจสอบว่าการลงทะเบียนถูกลบและ Slot เพิ่มขึ้น
        self.assertTrue(Enrollment.objects.filter(user=self.user, quota=self.quota).exists())
        self.quota.refresh_from_db()
        self.assertEqual(self.quota.Slot, 31)  # Slot ควรเพิ่มขึ้น 1

    def test_registed_quota(self):
        """ลงทะเบียนวิชาเรียนซ้ำ"""
        Enrollment.objects.create(user=self.user, quota=self.quota, approve='Pending')
        response = self.client.post(reverse('register_quota'), {'subject_id':self.quota.id})
        self.assertEqual(response.status_code, 302)
        

    def test_no_slot(self):
        """ลงทะเบียนโควต้าที่ slot เต็ม"""
        self.client.login(username='testuser', password='password')
        # สร้าง Quota ที่ไม่มี Slot
        self.quota.Slot = 0
        self.quota.save()
        response = self.client.post(reverse('register_quota'), {'subject_id': self.quota.id})
        self.assertEqual(response.status_code, 302)  # คาดว่าจะได้รับสถานะผิดพลาด
        

    def test_quota_not_found(self):
        """ไม่พบ Quota ที่ต้องการลงทะเบียน"""
        response = self.client.post(reverse('register_quota'), {'subject_id': 999})  # ใช้ ID ที่ไม่ถูกต้อง

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, "ไม่พบ Quota ที่ต้องการลงทะเบียน")
    
    def test_redirect_to_main_after_register(self):
        """ทดสอบว่า redirect ไปที่ main หลังจากทำการ GET"""
        # กรณีเมื่อ Slot เพียงพอและไม่มีการลงทะเบียนซ้ำ
        response = self.client.get(reverse('register_quota'))
        self.assertRedirects(response, reverse('main'))

    def test_cancel_quota_not_found(self):
        """ทดสอบกรณีไม่พบ Quota ที่ต้องการ"""
        # เข้าสู่ระบบผู้ใช้
        self.client.login(username='testuser', password='password')
        
        # ส่งคำขอเพื่อยกเลิก quota ที่ไม่มีอยู่ในระบบ
        response = self.client.post(reverse('cancel_quota'), {'subject_id': 999})  # ใช้ ID ที่ไม่มีอยู่
        
        # ตรวจสอบการ redirect ไปยังหน้าอื่น (เช่น หน้า 'main')
        self.assertRedirects(response, reverse('history'))
    
# class SubjectView(TestCase):
#     def setUp(self):
#         self.quota = Quota.objects.create(Subject='Test Subject', Year=2024, Semester=1, Slot=1, Status='Available')

#     def test_subject_detail_view_with_existing_subject(self):
#         """ทดสอบการดึงข้อมูล subject ที่มีอยู่"""
#         response = self.client.get(reverse('subject_detail', kwargs= {'subject_id': self.quota.id}))
#         # ตรวจสอบว่าโหลดหน้าด้วย status code 200
#         self.assertEqual(response.status_code, 302)
        

#     # def test_subject_detail_view_with_nonexistent_subject(self):
#     #     """ทดสอบการดึงข้อมูล subject ที่ไม่มีอยู่ (ควร return 404)"""
#     #     non_existent_id = self.quota.id + 1  # ใช้ id ที่ไม่มีอยู่จริง
#     #     response = self.client.get(reverse('subject_detail', args=[non_existent_id]))
        
#     #     # ตรวจสอบว่า response เป็น 404 เมื่อ subject_id ไม่มีอยู่
#     #     self.assertEqual(response.status_code, 302)

        
        
class EnrollmentAdminTests(TestCase):

    def setUp(self):
        # สร้างผู้ใช้สำหรับการทดสอบและกำหนดสิทธิ์เป็น admin
        self.user = User.objects.create_superuser(username='admin', password='password')
        
        # สร้าง Quota สำหรับการทดสอบ
        self.quota = Quota.objects.create(
            Subject='Test Subject',
            Year=2024,
            Semester=1,
            Slot=5,
            Status='Available'
        )
        
        # สร้าง Enrollment สำหรับการทดสอบ
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            quota=self.quota,
            approve='Pending'
        )

    def test_approve_enrollment(self):
        """เข้าสู่ระบบด้วยผู้ใช้ admin"""
        self.client.login(username='admin', password='password')  
        
        # เรียกใช้ action approve_enrollment
        response = self.client.post(reverse('admin:Mywebsite_enrollment_changelist'), {
            'action': 'approve_enrollment',
            '_selected_action': [self.enrollment.id]
        })
        
        # ตรวจสอบว่า redirect ไปยังหน้าเป้าหมายหลังการดำเนินการ
        self.assertRedirects(response, reverse('admin:Mywebsite_enrollment_changelist'))
        
        # ตรวจสอบการเปลี่ยนแปลงสถานะการอนุมัติ
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.approve, 'Approved')
    
    def test_reject_enrollment(self):
        """เข้าสู่ระบบด้วยผู้ใช้ admin"""
        self.client.login(username='admin', password='password')  
    
    # เรียกใช้ action reject_enrollment
        response = self.client.post(reverse('admin:Mywebsite_enrollment_changelist'), {
            'action': 'reject_enrollment',
            '_selected_action': [self.enrollment.id]
        })
    
    # ตรวจสอบว่า redirect ไปยังหน้าเป้าหมายหลังการดำเนินการ
        self.assertRedirects(response, reverse('admin:Mywebsite_enrollment_changelist'))
    
    # ตรวจสอบการเปลี่ยนแปลงสถานะการอนุมัติ
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.approve, 'Rejected')
    
    # ตรวจสอบว่า Slot ใน Quota เพิ่มขึ้น
        self.quota.refresh_from_db()  # ทำการรีเฟรช Quota จากฐานข้อมูล
        self.assertEqual(self.quota.Slot, 6)  # Slot ควรเพิ่มขึ้น 1


    def test_enrollment_display_in_admin(self):
        """เข้าสู่ระบบด้วยผู้ใช้ admin"""
        self.client.login(username='admin', password='password')  
        
        response = self.client.get(reverse('admin:Mywebsite_enrollment_changelist'))  # เข้าถึงหน้ารายการ Enrollment
        self.assertEqual(response.status_code, 200)  # ตรวจสอบว่ารหัสสถานะคือ 200
        self.assertContains(response, self.user.username)  # ตรวจสอบว่ามีชื่อผู้ใช้ในรายการ