import os
import subprocess
from django.conf import settings

# Variable global para cachear la versión y no ejecutar git/leer archivo en cada petición
_APP_VERSION_CACHE = None

def get_app_version():
    global _APP_VERSION_CACHE
    if _APP_VERSION_CACHE is not None:
        return _APP_VERSION_CACHE
        
    try:
        # Intenta obtener la versión desde git
        version_tag = subprocess.check_output(
            ['git', 'describe', '--tags', '--always'], 
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        commit_info = subprocess.check_output(
            ['git', 'log', '-1', '--format=%cd - %s', '--date=short'], 
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        _APP_VERSION_CACHE = f"{version_tag} ({commit_info})"
    except Exception:
        # Si git falla (ej: dentro del Docker), intenta leer el archivo APP_VERSION.txt
        version_file = os.path.join(settings.BASE_DIR, 'APP_VERSION.txt')
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                _APP_VERSION_CACHE = f.read().strip()
        else:
            _APP_VERSION_CACHE = os.environ.get('APP_VERSION', 'Desconocida')
            
    return _APP_VERSION_CACHE

def entorno(request):
    return {
        'ENTORNO': settings.ENTORNO,
        'APP_VERSION': get_app_version()
    }
