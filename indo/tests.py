from django.test import SimpleTestCase
from django.urls import resolve, reverse

from .views import HomePageView


class HomeTests(SimpleTestCase):
    def test_root_url_resolves_to_homepage_view(self):
        found = resolve('/')
        self.assertEqual(found.func.__name__, HomePageView.as_view().__name__)
        self.assertEqual(found.view_name, 'home')

    def test_home_page_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_by_name(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('home'))
        self.assertTemplateUsed(resp, 'home.html')

    def test_home_page_returns_correct_html(self):
        response = self.client.get('/')
        html = response.content.decode('utf-8')
        self.assertTrue(html.startswith('<!DOCTYPE html>'))
        self.assertIn('<title>Proyectos de Innovación Docente</title>', html)
        self.assertTrue(html.endswith('</html>\n'))


class AyudaTest(SimpleTestCase):
    def test_view_url_exists_at_proper_location(self):
        response = self.client.get('/ayuda/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_by_name(self):
        resp = self.client.get(reverse('ayuda'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('ayuda'))
        self.assertTemplateUsed(resp, 'ayuda.html')
