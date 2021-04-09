from pathlib import Path

from huey.contrib.djhuey import task
from weasyprint import HTML  # https://weasyprint.org/


@task()
def generar_pdf(url_origen, pdf_destino):
    """Obtiene una página web y la guarda en formato PDF en la ruta indicada."""
    html = HTML(url_origen)
    # Si no existe el directorio del PDF destino, crearlo recursivamente.
    Path(pdf_destino).parent.mkdir(parents=True, exist_ok=True)
    html.write_pdf(pdf_destino)
