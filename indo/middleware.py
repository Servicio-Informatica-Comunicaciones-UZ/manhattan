from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin

class ImpersonateMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.is_impersonating = False
        request.real_user = request.user
        
        impersonate_id = request.session.get('impersonate_id')
        
        # Solo los administradores de suplantación pueden suplantar. Comprobamos los permisos del usuario real (el que inició sesión).
        if impersonate_id and request.user.is_authenticated and request.user.has_perm('indo.suplantar_usuario'):
            User = get_user_model()
            try:
                impersonated_user = User.objects.get(pk=impersonate_id)
                request.user = impersonated_user
                request.is_impersonating = True
            except User.DoesNotExist:
                # Si el usuario ya no existe, limpiar la sesión
                del request.session['impersonate_id']
