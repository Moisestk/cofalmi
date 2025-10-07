from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from functools import wraps
from .models import Bitacora
from django.utils import timezone

def registrar_bitacora(accion, tipo_objeto, descripcion, objeto_id=None, objeto_nombre=None, request=None):
    """
    Función para registrar actividades en la bitácora del sistema
    """
    try:
        # Obtener información del request si está disponible
        usuario = None
        ip_address = None
        user_agent = None
        
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            usuario = request.user
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limitar a 500 caracteres
        
        # Crear registro de bitácora
        Bitacora.objects.create(
            usuario=usuario,
            accion=accion,
            tipo_objeto=tipo_objeto,
            descripcion=descripcion,
            objeto_id=objeto_id,
            objeto_nombre=objeto_nombre,
            ip_address=ip_address,
            user_agent=user_agent
        )
    except Exception as e:
        # Log del error sin interrumpir el flujo principal
        print(f"Error al registrar bitácora: {e}")

def get_client_ip(request):
    """
    Obtiene la IP real del cliente considerando proxies
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_action(accion, tipo_objeto, descripcion_template, objeto_id_field=None, objeto_nombre_field=None):
    """
    Decorador para registrar automáticamente acciones en la bitácora
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Ejecutar la función original
            response = func(request, *args, **kwargs)
            
            try:
                # Obtener información del objeto si está disponible
                objeto_id = None
                objeto_nombre = None
                
                # Intentar obtener el ID del objeto desde los argumentos o kwargs
                if objeto_id_field:
                    objeto_id = kwargs.get(objeto_id_field)
                
                if objeto_nombre_field:
                    objeto_nombre = kwargs.get(objeto_nombre_field)
                
                # Crear descripción
                descripcion = descripcion_template
                
                # Registrar en bitácora
                registrar_bitacora(
                    accion=accion,
                    tipo_objeto=tipo_objeto,
                    descripcion=descripcion,
                    objeto_id=objeto_id,
                    objeto_nombre=objeto_nombre,
                    request=request
                )
            except Exception as e:
                print(f"Error en decorador de bitácora: {e}")
            
            return response
        return wrapper
    return decorator

def superuser_required(view_func):
    """
    Decorador para verificar que el usuario sea superusuario
    """
    return user_passes_test(lambda u: u.is_authenticated and u.is_superuser)(view_func)

class SuperuserRequiredMixin:
    """
    Mixin para vistas basadas en clase que requieren superusuario
    """
    @method_decorator(superuser_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
