from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Quota, Enrollment
from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from .models import Quota
from .admin import QuotaAdmin

class QuotaAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.quota_admin = QuotaAdmin(Quota, self.site)
        self.quota = Quota.objects.create(
            Subject="Mathematics",
            Year=2023,
            Semester=1,
            Slot=30,
            Status="Open"
        )

    def test_admin_view(self):
        # Test displaying in the admin site
        self.assertEqual(str(self.quota), "Mathematics 2023 1 30 Open")


class QuotaViewTests(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(username="testuser", password="password")
        self.quota = Quota.objects.create(
            Subject="Mathematics",
            Year=2023,
            Semester=1,
            Slot=30,
            Status="Open"
        )

    def test_quota_list_view(self):
        response = self.client.get(reverse("quota_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mathematics")

    def test_quota_detail_view(self):
     
        response = self.client.get(reverse("quota_detail", args=[self.quota.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mathematics")

class EnrollmentViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.quota = Quota.objects.create(
            Subject="Mathematics",
            Year=2023,
            Semester=1,
            Slot=30,
            Status="Open"
        )
        self.client.login(username="testuser", password="password")

    def test_enrollment_create_view(self):
        response = self.client.post(reverse("enroll"), {"quota_id": self.quota.id})
        self.assertEqual(response.status_code, 302)  
        enrollment = Enrollment.objects.filter(user=self.user, quota=self.quota).exists()
        self.assertTrue(enrollment)
