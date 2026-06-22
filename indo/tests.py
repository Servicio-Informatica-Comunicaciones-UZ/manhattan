from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth import get_user_model
from datetime import date

from .views import HomePageView
from .models import Convocatoria, Proyecto, ParticipanteProyecto, TipoParticipacion, Centro, Programa


class HomeTests(TestCase):
    def setUp(self):
        # Create a convocatoria so Convocatoria.get_ultima() doesn't fail
        self.convocatoria = Convocatoria.objects.create(
            id=date.today().year,
            permite_colaboradores=True
        )

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


class AyudaTest(TestCase):
    def setUp(self):
        # Create a convocatoria so Convocatoria.get_ultima() doesn't fail
        self.convocatoria = Convocatoria.objects.create(
            id=date.today().year,
            permite_colaboradores=True
        )

    def test_view_url_exists_at_proper_location(self):
        response = self.client.get('/ayuda/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_by_name(self):
        resp = self.client.get(reverse('ayuda'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('ayuda'))
        self.assertTemplateUsed(resp, 'ayuda.html')


class CollaboratorsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user_f = User.objects.create_user(username='111111', first_name='Maria', last_name='F', email='maria@example.com', sexo='F')
        self.user_m = User.objects.create_user(username='222222', first_name='Juan', last_name='M', email='juan@example.com', sexo='M')
        
        self.tipo_colaborador = TipoParticipacion.objects.get_or_create(nombre='colaborador')[0]
        self.tipo_participante = TipoParticipacion.objects.get_or_create(nombre='participante')[0]
        self.tipo_coordinador = TipoParticipacion.objects.get_or_create(nombre='coordinador')[0]
        
        self.convocatoria_no = Convocatoria.objects.create(id=2025, permite_colaboradores=False)
        self.convocatoria_yes = Convocatoria.objects.create(id=2026, permite_colaboradores=True)
        
        self.centro = Centro.objects.create(nombre='Centro Test', academico_id_nk=1, rrhh_id_nk='1')
        self.programa_no = Programa.objects.create(nombre_corto='P1', nombre_largo='P1', convocatoria=self.convocatoria_no, campos='["contexto"]')
        self.programa_yes = Programa.objects.create(nombre_corto='P2', nombre_largo='P2', convocatoria=self.convocatoria_yes, campos='["contexto"]')
        
        self.proyecto_no = Proyecto.objects.create(
            titulo='Proyecto Sin Colaboradores',
            convocatoria=self.convocatoria_no,
            centro=self.centro,
            programa=self.programa_no
        )
        
        self.proyecto_yes = Proyecto.objects.create(
            titulo='Proyecto Con Colaboradores',
            convocatoria=self.convocatoria_yes,
            centro=self.centro,
            programa=self.programa_yes
        )

    def test_get_cargo_returns_correct_collaborator_string_by_gender(self):
        # Female collaborator
        pp_f = ParticipanteProyecto.objects.create(
            proyecto=self.proyecto_yes,
            tipo_participacion=self.tipo_colaborador,
            usuario=self.user_f
        )
        self.assertEqual(pp_f.get_cargo(), 'Colaboradora')
        
        # Male collaborator
        pp_m = ParticipanteProyecto.objects.create(
            proyecto=self.proyecto_yes,
            tipo_participacion=self.tipo_colaborador,
            usuario=self.user_m
        )
        self.assertEqual(pp_m.get_cargo(), 'Colaborador')

    def test_permite_colaboradores_default_false(self):
        conv = Convocatoria.objects.create(id=2027)
        self.assertFalse(conv.permite_colaboradores)
