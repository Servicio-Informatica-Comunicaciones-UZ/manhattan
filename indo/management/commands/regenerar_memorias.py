import os
from django.core.management.base import BaseCommand
from django.conf import settings
from indo.models import Proyecto
from indo.tasks import generar_pdf

class Command(BaseCommand):
    help = 'Regenera los PDFs de las memorias de una convocatoria y los envía a procesar a la cola'

    def add_arguments(self, parser):
        parser.add_argument('--anyo', type=int, required=True, help='ID de la convocatoria (año)')
        parser.add_argument('--base-url', type=str, required=True, help='URL base (ej: https://manhattan.unizar.es)')
        parser.add_argument('--forzar', action='store_true', help='Regenerar todos aunque el PDF ya exista')

    def handle(self, *args, **options):
        id_convocatoria = options['anyo']
        url_base_sitio = options['base_url'].rstrip('/')
        forzar = options['forzar']

        proyectos_con_memoria = Proyecto.objects.filter(
            convocatoria_id=id_convocatoria,
            estado__in=['MEM_PRESENTADA', 'MEM_ADMITIDA', 'MEM_NO_ADMITIDA']
        )

        self.stdout.write(self.style.SUCCESS(
            f"Encontrados {proyectos_con_memoria.count()} proyectos en la convocatoria {id_convocatoria} con memoria presentada."
        ))

        for proyecto in proyectos_con_memoria:
            proyecto_id = proyecto.id
            base_url = f"{url_base_sitio}/memoria/{proyecto_id}/"
            
            pdf_destino = os.path.join(
                settings.MEDIA_ROOT,
                'memoria',
                str(proyecto.convocatoria_id),
                f'{proyecto.programa.nombre_corto}_{proyecto_id}.pdf',
            )
            
            if not os.path.exists(pdf_destino) or forzar:
                accion = "Sobreescribiendo" if os.path.exists(pdf_destino) else "Falta el PDF. Encolando generación"
                self.stdout.write(f"[{proyecto_id}] {accion} para '{proyecto.titulo[:30]}...'")
                
                # Envía la tarea a la cola de Huey
                generar_pdf(proyecto_id, base_url, pdf_destino)
