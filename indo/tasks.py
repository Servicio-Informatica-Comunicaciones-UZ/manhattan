from pathlib import Path

from huey.contrib.djhuey import task


@task()
def generar_pdf(documento_html, pdf_destino):
    """Recibe un documento HTML y lo guarda en formato PDF en la ruta indicada."""
    # Si no existe el directorio del PDF destino, crearlo recursivamente.
    Path(pdf_destino).parent.mkdir(parents=True, exist_ok=True)

    documento_html.write_pdf(pdf_destino)
