from django.test import SimpleTestCase
from django.urls import reverse


class HomeTests(SimpleTestCase):
    def test_home_page_status_code(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_by_name(self):
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "home.html")


class AyudaTest(SimpleTestCase):
    def test_view_url_exists_at_proper_location(self):
        response = self.client.get("/ayuda/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_by_name(self):
        resp = self.client.get(reverse("ayuda"))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse("ayuda"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "ayuda.html")
