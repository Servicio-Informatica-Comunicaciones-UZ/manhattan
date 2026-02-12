from django.conf import settings

def entorno(request):
    return {'ENTORNO': settings.ENTORNO}
