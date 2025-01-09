from django.test import TestCase
from django.contrib.auth.models import User
from .models import Quota, Profile, Enrollment
from django.urls import reverse


class MyViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.quota = Quota.objects.create(Subject='Test Subject', Year=2024, Semester=1, Slot=1, Status='Available')

    def test_login_view_requires_login(self):
        """"ทดสอบว่าหน้าล็อกอินสามารถเข้าถึงได้หรือไม่"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")   

    def test_successful_login(self):
        """ทดสอบการล็อกอินที่สำเร็จ"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password'
        })
        self.assertRedirects(response, reverse('main'))  

    def test_failed_login(self):
        """ทดสอบการล็อกอินที่ไม่สำเร็จ"""
        response = self.client.post(reverse('login'),{
            'username': 'wronguser',  
            'password': 'wrongpassword' 
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
        self.assertContains(response, "Passwords do not match.")  

    def test_successful_registration(self):
        """ทดสอบการลงทะเบียนที่สำเร็จ"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'newpassword',
            'confirm_password': 'newpassword'
        })
        self.assertRedirects(response, reverse('login'))  
        new_user = User.objects.get(username='newuser')  
        self.assertIsNotNone(new_user)

    def test_failed_registration_duplicate_username(self):
        """"ทดสอบการลงทะเบียนที่ล้มเหลวเนื่องจากชื่อผู้ใช้ซ้ำ"""
        response = self.client.post(reverse('register'), {
            'username': 'testuser', 
            'password': 'password',
            'confirm_password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "An error occurred") 

    def test_successful_register_quota(self):
        """ทดสอบการลงทะเบียน Quota ที่สำเร็จ"""
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('register_quota'), {'subject_id': self.quota.id})
        self.assertRedirects(response, reverse('main'))  
        enrollment = Enrollment.objects.filter(user=self.user, quota=self.quota).first() 
        self.assertIsNotNone(enrollment)

class QuotaModelTest(TestCase):
    def setUp(self):
        
        self.quota = Quota.objects.create(
            Subject="Mathematics",
            Year=2023,
            Semester=1,
            Slot=30,
            Status="Open"
        )

    def test_quota_creation(self):
        """"ทดสอบการสร้าง Quota"""
        self.assertTrue(isinstance(self.quota, Quota))  
        self.assertEqual(self.quota.__str__(), "Mathematics 2023 1 30 Open") 

class ProfileModelTest(TestCase):

    def setUp(self):
        # สร้างผู้ใช้และโปรไฟล์สำหรับการทดสอบ
        self.user = User.objects.create_user(username="testuser", password="password")
        self.profile = Profile.objects.create(user=self.user)

    def test_profile_creation(self):
        """ทดสอบการสร้างโปรไฟล์"""
        self.assertTrue(isinstance(self.profile, Profile))  
        self.assertEqual(self.profile.__str__(), "testuser") 

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
    def test_cancel_no_enrollment(self):
        """ไม่พบการลงทะเบียนในโควต้าที่ยกเลิก"""
        response = self.client.post(reverse('cancel_quota'), {'subject_id': self.quota.id})
        self.assertRedirects(response,reverse('history'))

    def test_cancel_quota_not_found(self):
        """ทดสอบกรณีไม่พบ Quota ที่ต้องการ"""
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('cancel_quota'), {'subject_id': 999})  
        self.assertRedirects(response, reverse('history'))

    def test_cancel_quota_with_approved_status(self):
        """ทดสอบยกเลิกการลงทะเบียนที่อนุมัติแล้ว"""
        self.enrollment = Enrollment.objects.create(user=self.user, quota=self.quota, approve="Approve")
        response = self.client.post(reverse('cancel_quota'), {'subject_id': self.quota.id})
        self.assertRedirects(response, reverse('history'))  
        self.assertTrue(Enrollment.objects.filter(user=self.user, quota=self.quota).exists())
        self.quota.refresh_from_db()
        self.assertEqual(self.quota.Slot, 30)  

    def test_enrollment_creation(self):
        """ทดสอบการสร้างการลงทะเบียน"""
        self.enrollment = Enrollment.objects.create(user=self.user, quota=self.quota, approve="Pending")
        self.assertTrue(isinstance(self.enrollment, Enrollment))  
        self.assertEqual(self.enrollment.__str__(), "testuser enrolled in Mathematics")  
        self.assertEqual(self.enrollment.approve, "Pending")  
    
    def test_successful_cancel_quota(self):
        """ทดสอบการยกเลิกการลงทะเบียน Quota """
        self.enrollment = Enrollment.objects.create(user=self.user, quota=self.quota, approve="Pending")
        response = self.client.post(reverse('cancel_quota'), {'subject_id': self.quota.id})
        self.assertRedirects(response, reverse('history'))  
        self.assertFalse(Enrollment.objects.filter(user=self.user, quota=self.quota).exists())
        self.quota.refresh_from_db()
        self.assertEqual(self.quota.Slot, 31)  

    def test_registed_quota(self):
        """ลงทะเบียนวิชาเรียนซ้ำ"""
        Enrollment.objects.create(user=self.user, quota=self.quota, approve='Pending')
        response = self.client.post(reverse('register_quota'), {'subject_id':self.quota.id})
        self.assertEqual(response.status_code, 302)
        

    def test_no_slot(self):
        """ลงทะเบียนโควต้าที่ slot เต็ม"""
        self.client.login(username='testuser', password='password')
        self.quota.Slot = 0
        self.quota.save()
        response = self.client.post(reverse('register_quota'), {'subject_id': self.quota.id})
        self.assertEqual(response.status_code, 302)  
        

    def test_quota_not_found(self):
        """ไม่พบ Quota ที่ต้องการลงทะเบียน"""
        response = self.client.post(reverse('register_quota'), {'subject_id': 999})  

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(messages[0].message, "ไม่พบ Quota ที่ต้องการลงทะเบียน")
    
    def test_redirect_to_main_after_register(self):
        """ทดสอบว่า redirect ไปที่ main หลังจากทำการ GET"""
       
        response = self.client.get(reverse('register_quota'))
        self.assertRedirects(response, reverse('main'))

class SubjectView(TestCase):
    def setUp(self):
        self.quota = Quota.objects.create(
            Subject="Mathematics",
            Year=2023,
            Semester=1,
            Slot=30,
            Status="Open" 
        )
        self.user = User.objects.create_superuser(username='admin', password='password')
    def test_subject_detail_view_exists(self):
            """ทดสอบว่าหน้ารายละเอียดวิชาเข้าถึงได้"""
            self.client.login(username='admin', password='password')  
            response = self.client.get(reverse('subject_detail', args=(self.quota.id,)))
            self.assertEqual(response.status_code, 200)
            
        
        
class EnrollmentAdminTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(username='admin', password='password')
        self.quota = Quota.objects.create(
            Subject='Test Subject',
            Year=2024,
            Semester=1,
            Slot=5,
            Status='Available'
        )
        
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            quota=self.quota,
            approve='Pending'
        )

    def test_approve_enrollment(self):
        """เข้าสู่ระบบด้วยผู้ใช้ admin"""
        self.client.login(username='admin', password='password')  
        response = self.client.post(reverse('admin:Mywebsite_enrollment_changelist'), {
            'action': 'approve_enrollment',
            '_selected_action': [self.enrollment.id]
        })
        self.assertRedirects(response, reverse('admin:Mywebsite_enrollment_changelist'))
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.approve, 'Approved')
    
    def test_reject_enrollment(self):
        """เข้าสู่ระบบด้วยผู้ใช้ admin"""
        self.client.login(username='admin', password='password')  
        response = self.client.post(reverse('admin:Mywebsite_enrollment_changelist'), {
            'action': 'reject_enrollment',
            '_selected_action': [self.enrollment.id]
        })
        self.assertRedirects(response, reverse('admin:Mywebsite_enrollment_changelist'))
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.approve, 'Rejected')
        self.quota.refresh_from_db()  
        self.assertEqual(self.quota.Slot, 6)  


    def test_enrollment_display_in_admin(self):
        """เข้าสู่ระบบด้วยผู้ใช้ admin"""
        self.client.login(username='admin', password='password')  
        response = self.client.get(reverse('admin:Mywebsite_enrollment_changelist')) 
        self.assertEqual(response.status_code, 200)  
        self.assertContains(response, self.user.username) 