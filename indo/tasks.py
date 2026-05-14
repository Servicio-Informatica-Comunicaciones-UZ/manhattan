from pathlib import Path

from huey.contrib.djhuey import task
from django.template.loader import render_to_string

from weasyprint import HTML


@task()
def generar_pdf(proyecto_id, base_url, pdf_destino):
    """Recibe un proyecto_id y base_url, renderiza el HTML y lo guarda en formato PDF."""
    from indo.models import Proyecto
    proyecto = Proyecto.objects.get(pk=proyecto_id)
    contexto = {
        'anyo': proyecto.convocatoria.id,
        'proyecto': proyecto,
        'apartados': proyecto.convocatoria.apartados_memoria.all(),
        'dict_respuestas': proyecto.get_dict_respuestas_memoria(),
    }
    html_string = render_to_string('memoria/detail.html', context=contexto)

    # Si no existe el directorio del PDF destino, crearlo recursivamente.
    Path(pdf_destino).parent.mkdir(parents=True, exist_ok=True)

    documento_html = HTML(string=html_string, base_url=base_url)
    documento_html.write_pdf(pdf_destino)
