from uu import encode
from django.shortcuts import render, redirect, get_object_or_404
from django.http import  HttpResponse, JsonResponse
from corfalmi import settings
from .models import (
     Perfil, Configuracion, Encuesta, Fotografia, ItemEncuesta, ItemRespuesta, Encuestado, Respuesta, OpcionPregunta, Bitacora
)
from .forms import (
    FormularioActualizarPerfil, FormularioCambiarPassword, FormularioEditarUsuario, FormularioPerfil, FormularioResgistrarUsuario,
    AdminUserChangeForm, AdminPasswordChangeForm, ConfiguracionForm,
    EncuestaForm, FotografiaForm, RespuestaForm, ItemEncuestaForm, ItemRespuestaForm, EncuestadoForm, CustomSetPasswordForm, LoginForm                 
)
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from datetime import date, datetime, timedelta
from django.contrib.auth import authenticate, login as auth_login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import PasswordResetForm
from axes.models import AccessAttempt
from axes.handlers.proxy import AxesProxyHandler
from django.urls import reverse
from xhtml2pdf import pisa
from django.template.loader import get_template, render_to_string
from collections import OrderedDict
from django.db.models import Q
from django.db import models
from django.db.models import Avg, F, ExpressionWrapper, Count
from .utils import registrar_bitacora
from django.shortcuts import redirect
import json
from django.db.models.functions import TruncDate
from django.utils import timezone
from axes.helpers import get_failure_limit


def custom_csrf_failure(request, reason=""):
    return render(request, "paginas/error_csrf.html", {"reason": reason}, status=403)

def is_superuser(user):
    return user.is_superuser
 
# def configuracion(request):
def configuracion(request):
    configuracion = Configuracion.objects.first()
    if request.method == 'POST':
        form = ConfiguracionForm(request.POST, request.FILES, instance=configuracion)
        if form.is_valid():
            form.save()
            return redirect('configuracion')
    else:
        form = ConfiguracionForm(instance=configuracion)
    return render(request, 'Corporacion/Configuracion/configuracion.html', {'form': form})



#Proteger la vista de inicio

@login_required
def inicio(request):
    # Rango de los últimos 30 días (en zona local)
    today = timezone.localdate()
    dias = [today - timedelta(days=i) for i in range(29, -1, -1)]
    dias_str = [d.strftime('%Y-%m-%d') for d in dias]

    # Usar SQL directo para obtener datos por día
    from django.db import connection
    
    # Encuestas por día usando SQL directo
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DATE(fecha_creacion) as dia, COUNT(*) as total 
            FROM encuesta_encuesta 
            WHERE papelera = 0 AND DATE(fecha_creacion) >= %s 
            GROUP BY DATE(fecha_creacion) 
            ORDER BY dia
        """, [dias[0]])
        encuestas_por_dia = cursor.fetchall()
    
    encuestas_dict = {e[0].strftime('%Y-%m-%d'): e[1] for e in encuestas_por_dia}
    data_encuestas = [encuestas_dict.get(d, 0) for d in dias_str]

    # Encuestados por día usando SQL directo
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DATE(fecha_registro) as dia, COUNT(*) as total 
            FROM encuesta_encuestado 
            WHERE papelera = 0 AND DATE(fecha_registro) >= %s 
            GROUP BY DATE(fecha_registro) 
            ORDER BY dia
        """, [dias[0]])
        encuestados_por_dia = cursor.fetchall()
    
    encuestados_dict = {e[0].strftime('%Y-%m-%d'): e[1] for e in encuestados_por_dia}
    data_encuestados = [encuestados_dict.get(d, 0) for d in dias_str]

    # Fotografías por día usando SQL directo
    from .models import Fotografia
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DATE(fecha_subida) as dia, COUNT(*) as total 
            FROM encuesta_fotografia 
            WHERE DATE(fecha_subida) >= %s 
            GROUP BY DATE(fecha_subida) 
            ORDER BY dia
        """, [dias[0]])
        fotografias_por_dia = cursor.fetchall()
    
    fotografias_dict = {f[0].strftime('%Y-%m-%d'): f[1] for f in fotografias_por_dia}
    data_fotografias = [fotografias_dict.get(d, 0) for d in dias_str]

    # Totales
    total_encuestas = Encuesta.objects.filter(papelera=False).count()
    total_encuestados = Encuestado.objects.filter(papelera=False).count()
    total_fotografias = Fotografia.objects.count()


    return render(request, 'inicio.html', {
        'total_encuestas': total_encuestas,
        'total_encuestados': total_encuestados,
        'total_fotografias': total_fotografias,
        'labels_grafico': json.dumps(dias_str),
        'data_encuestas': json.dumps(data_encuestas),
        'data_encuestados': json.dumps(data_encuestados),
        'data_fotografias': json.dumps(data_fotografias),
    })


    
 #Cerrar sesión
@csrf_exempt
def logout_view(request):
    # Registrar logout en bitácora antes de hacer logout
    if request.user.is_authenticated:
        registrar_bitacora(
            accion='cerrar_sesion',
            tipo_objeto='usuario',
            descripcion=f'Usuario {request.user.username} cerró sesión',
            objeto_id=request.user.id,
            objeto_nombre=request.user.username,
            request=request
        )
    
    logout(request)
    return redirect('login_view')
 
def login(request):
    configuracion= Configuracion.objects.all() 
    print(configuracion)
    return render(request, 'Usuario/login.html',{"configuracion":configuracion})

def axes_lockout(request, credentials=None, *args, **kwargs):
    messages.error(request, "Tu cuenta ha sido bloqueada. Contacta a un administrador para desbloquearla.")
    configuracion = Configuracion.objects.first()
    form = LoginForm()
    return render(request, 'Usuario/login.html', {
        "configuracion": configuracion,
        "form": form,
        "attempts_left": None,
    })

def login_view(request):
    configuracion = Configuracion.objects.first()
    form = LoginForm(request.POST or None)
    attempts_left = None

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password'].strip()
            user_obj = User.objects.filter(username=username).first()

            # Verifica si el usuario está bloqueado por Axes
            if AxesProxyHandler.is_locked(request, credentials={'username': username}):
                messages.error(request, 'Tu cuenta ha sido bloqueada. Contacta a un administrador para desbloquearla.')
                return render(request, 'Usuario/login.html', {
                    "configuracion": configuracion,
                    "form": form,
                    "attempts_left": attempts_left,
                })

            user = authenticate(request, username=username, password=password)
            # Solo calcula los intentos si el usuario existe y está activo
            if user_obj:
                if not user_obj.is_active:
                    messages.error(request, 'Tu usuario está bloqueado. Contacta al administrador.')
                    # No calcular ni mostrar intentos fallidos
                    return render(request, 'Usuario/login.html', {"configuracion": configuracion, "form": form})
                failure_limit = get_failure_limit(request, credentials={'username': username})
                attempt = AccessAttempt.objects.filter(username=username, failures_since_start__gt=0).order_by('-attempt_time').first()
                current_failures = attempt.failures_since_start if attempt else 0
                attempts_left = max(failure_limit - current_failures, 0)
            if user is not None:
                auth_login(request, user)
                # Registrar login exitoso en bitácora
                registrar_bitacora(
                    accion='iniciar_sesion',
                    tipo_objeto='usuario',
                    descripcion=f'Usuario {username} inició sesión exitosamente',
                    objeto_id=user.id,
                    objeto_nombre=username,
                    request=request
                )
                return redirect('inicio')
            else:
                # Mensaje genérico, no revela si el usuario existe o no
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Verifica los datos y resuelve el captcha correctamente.')

    return render(request, 'Usuario/login.html', {
        "configuracion": configuracion,
        "form": form,
        "attempts_left": attempts_left,
    })

# Recuperar contraseña
def password_reset_confirm(request, uidb64=None, token=None):
    if request.method == 'POST':
        form = CustomSetPasswordForm(user, request.POST or None)
        email = request.POST.get('email', '').strip()
        user = User.objects.filter(email=email).first()
        if user and not user.is_active:
            messages.error(request, 'Tu usuario está bloqueado. Contacta al superadministrador.')
            return render(request, 'registration/password_reset_1.html', {'form': form})
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='registration/password_reset_email.html'
            )
            messages.success(request, 'Si el correo existe y está habilitado, recibirás instrucciones para recuperar tu contraseña.')
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    return render(request, 'registration/password_reset_1.html', {'form': form})

from django.contrib.auth.views import PasswordResetConfirmView
from .forms import CustomSetPasswordForm

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'registration/password_reset_confirm1.html'



def index(request):
    return render(request, 'Usuario/usuarios/index.html')


@login_required
def usuarios(request):

    if request.user.is_staff:
        user = request.user
        grupo = obtenerGrupo(user)
        listaUsuarios = Perfil.objects.select_related('usuario').all()
        print(listaUsuarios)  # Imprime para verificar los datos
        usuarios = []
        for perfil in listaUsuarios:
            try:
                tipo = Group.objects.get(user=perfil.usuario.id).name
            except Exception as e:
                print(e)  # Imprime el error
                tipo = ""
            if tipo != "" and perfil.usuario.id != request.user.id:
                usuarios.append({
                    "id": perfil.usuario.id,
                    "avatar": perfil.avatar,
                    "nombre": perfil.usuario.first_name,
                    "apellido": perfil.usuario.last_name,
                    "correo": perfil.usuario.email,
                    "tipo": tipo,
                    "estado": perfil.usuario.is_active,
                })
        print(usuarios)  # Imprime para verificar los datos antes de enviar a la plantilla
        return render(request, 'Usuario/usuarios/index.html', {'usuarios': usuarios, 'grupo': grupo})

    
@login_required
def nuevoUsuario(request):
    if request.user.is_staff:
        grupos = Group.objects.all()
        form = FormularioResgistrarUsuario(request.POST)
        if request.POST:
            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password1']
                group = Group.objects.get(name=form.cleaned_data['grupo'])
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                user = User.objects.create_user(
                    username=username, email=email, password=password, first_name=first_name, last_name=last_name)
                user.groups.add(group)
                user.save()
                perfil = Perfil.objects.get(usuario=user.id)
                perfil.save()
                
                # Registrar creación de usuario en bitácora
                registrar_bitacora(
                    accion='crear',
                    tipo_objeto='usuario',
                    descripcion=f'Se creó el usuario "{username}" con grupo "{group.name}"',
                    objeto_id=user.id,
                    objeto_nombre=username,
                    request=request
                )
                
                return redirect('usuarios')
        else:
            form = FormularioResgistrarUsuario()
        return render(request, 'Usuario/usuarios/nuevo.html', {'form': form,"grupos":grupos})

def obtenerGrupo(user):
    try:
        grupo = user.groups.all()[0]
        return str(grupo)
    except:
        return "Super Usuario"    

@login_required
def editarUsuario(request, id):
    if request.user.is_staff:
        try:
            usuario = User.objects.get(id=id)
            perfil = Perfil.objects.get(usuario=usuario.id)
            grupo = Group.objects.get(user=usuario.id).name
        except:
            usuario = ""
        if usuario:
            grupos = Group.objects.all()
            if request.method == 'POST':
                post_data = request.POST.copy()
                # Si el campo username no viene en el POST, lo rellenamos con el valor actual
                if 'username' not in post_data or not post_data['username']:
                    post_data['username'] = usuario.username
                # Si el campo grupo no viene en el POST, lo rellenamos con el valor actual
                if 'grupo' not in post_data or not post_data['grupo']:
                    post_data['grupo'] = grupo
                form = FormularioEditarUsuario(post_data, instance=usuario)
                if form.is_valid():
                    username = form.cleaned_data['username']
                    email = form.cleaned_data['email']
                    group = Group.objects.get(name=form.cleaned_data['grupo'])
                    first_name = form.cleaned_data['first_name']
                    last_name = form.cleaned_data['last_name']
                    # Si tienes fechaExpiracion, asegúrate de que esté en el formulario
                    fechaExpiracion = getattr(form.cleaned_data, 'fechaExpiracion', None)
                    usuario.username = username
                    usuario.email = email
                    usuario.first_name = first_name
                    usuario.last_name = last_name
                    usuario.is_active = True
                    usuario.groups.clear()
                    usuario.groups.add(group)
                    usuario.save()
                    perfil = Perfil.objects.get(usuario=usuario.id)
                    if fechaExpiracion:
                        perfil.fechaExpiracion = fechaExpiracion
                        perfil.save()
                    
                    # Registrar edición de usuario en bitácora
                    registrar_bitacora(
                        accion='editar',
                        tipo_objeto='usuario',
                        descripcion=f'Se editó el usuario "{username}" - grupo: "{group.name}"',
                        objeto_id=usuario.id,
                        objeto_nombre=username,
                        request=request
                    )
                    
                    return redirect('usuarios')
            else:
                # Pasa el grupo actual como valor inicial
                form = FormularioEditarUsuario(instance=usuario, initial={'grupo': grupo})
            return render(request, 'Usuario/usuarios/editar.html', {
    'form': form,
    'perfil': perfil,
    'grupos': grupos,
    'grupoUsuario': grupo,
    'editar': True
})
        else:
            mensaje = "El usuario no existe."
            return render(request, 'paginas/restringido/restringido.html', {'mensaje': mensaje})
    else:
        mensaje = "No tiene los privilegios suficientes para realizar esta acción."
        return render(request, 'paginas/restringido/restringido.html', {'mensaje': mensaje})
    
            
@login_required
def borrar_usuario(request, usuario_id):
    if not request.user.is_superuser:
        messages.error(request, "Solo el superadministrador puede eliminar usuarios.")
        return redirect('usuarios')

    usuario = get_object_or_404(User, id=usuario_id)

    if request.method == 'POST':
        password = request.POST.get('password', '')
        user = authenticate(request, username=request.user.username, password=password) 
        if user is None:
            messages.error(request, "Contraseña incorrecta.")
            return render(request, 'Usuario/usuarios/borrar.html')
        username_usuario = usuario.username
        usuario.delete()
        
        # Registrar eliminación de usuario en bitácora
        registrar_bitacora(
            accion='eliminar',
            tipo_objeto='usuario',
            descripcion=f'Se eliminó el usuario "{username_usuario}"',
            objeto_id=usuario_id,
            objeto_nombre=username_usuario,
            request=request
        )
        
        messages.success(request, "Usuario eliminado correctamente.")
        return redirect('usuarios')

    return render(request, 'Usuario/usuarios/borrar.html')

@login_required
def habilitarInhabilitarUsuario(request, accion, id):
    if request.user.is_staff:
        usuario = User.objects.get(id=id)
        if accion == "habilitar":
            usuario.is_active = True
            accion_desc = "habilitó"
        else:
            usuario.is_active = False
            accion_desc = "deshabilitó"
        usuario.save()
        
        # Registrar habilitación/deshabilitación de usuario en bitácora
        registrar_bitacora(
            accion='activar' if accion == "habilitar" else 'desactivar',
            tipo_objeto='usuario',
            descripcion=f'Se {accion_desc} el usuario "{usuario.username}"',
            objeto_id=usuario.id,
            objeto_nombre=usuario.username,
            request=request
        )
        
        return HttpResponse('correcto')
    else:
        return render(request, 'paginas/restringido/restringido.html')

@login_required
def cambiarPassword(request, id):
    if request.user.is_staff:
        usuario = User.objects.get(id=id)
        form = FormularioCambiarPassword(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                nuevo_password = form.cleaned_data['password']
                usuario.set_password(nuevo_password)
                usuario.save()
                messages.success(request, '¡Contraseña cambiada exitosamente!')
                return redirect('usuarios')
            else:
                messages.error(request, 'Hubo un error al cambiar la contraseña. Por favor, verifica los campos.')
        return render(request, 'Usuario/admin1/cambiarPasswordUsuario.html', {'form': form, 'usuario': usuario})
    else:
        messages.error(request, 'No tienes permisos para cambiar la contraseña.')
        return redirect('usuarios')

@login_required
def perfil(request):
    usuario = User.objects.get(id=request.user.id)
    grupo = ""
    try:
        user = request.user
        grupo = obtenerGrupo(user)
        perfil = Perfil.objects.get(usuario=request.user.id)
        form = FormularioPerfil(
            request.POST or None, request.FILES or None, instance=perfil)
    except:
        perfil = {
            'usuario': request.user.id,
            'avatar': None,
        }
        form = FormularioPerfil(
            request.POST or None, request.FILES or None)
    formUsuario = FormularioActualizarPerfil(
        request.POST or None, instance=usuario)
    if request.POST:
        if formUsuario.is_valid() and form.is_valid():
            formUsuario.save()
            form.save()
            return redirect('perfil')
        else:
            form = FormularioPerfil()
    return render(request, 'paginas/perfil/index.html', {'formPerfil': form, 'formUsuario': formUsuario, 'usuario': usuario, 'grupo': grupo})

@login_required
def perfil1(request):
    perfil_form = AdminUserChangeForm(instance=request.user)
    password_form = AdminPasswordChangeForm(user=request.user)
    active_tab = 'profile-overview'

    if request.method == 'POST':
        if 'editar_perfil' in request.POST:
            perfil_form = AdminUserChangeForm(request.POST, instance=request.user)
            password_form = AdminPasswordChangeForm(user=request.user)
            active_tab = 'profile-edit'
            if perfil_form.is_valid():
                perfil_form.save()
                messages.success(request, 'Perfil actualizado con éxito')
                return redirect('perfil1')
        elif 'cambiar_contraseña' in request.POST:
            perfil_form = AdminUserChangeForm(instance=request.user)
            password_form = AdminPasswordChangeForm(data=request.POST, user=request.user)
            active_tab = 'profile-change-password'
            if password_form.is_valid():
                try:
                    password_form.save()
                    update_session_auth_hash(request, password_form.user)
                    messages.success(request, 'Contraseña actualizada con éxito')
                    # Limpiar el formulario después del éxito
                    password_form = AdminPasswordChangeForm(user=request.user)
                except Exception as e:
                    messages.error(request, f'Error al cambiar la contraseña: {str(e)}')
            else:
                # Los errores se mostrarán automáticamente en el template
                pass

    return render(request, 'Usuario/perfil1.html', {
        'perfil_form': perfil_form,
        'password_form': password_form,
        'active_tab': active_tab
    })


# ----------------- PERSONA -----------------

@login_required
def listar_encuestados(request):
    encuestados = Encuestado.objects.filter(papelera=False)
    return render(request, 'encuestados/listar.html', {'encuestados': encuestados})

@login_required
def crear_encuestado(request):
    if request.method == 'POST':
        form = EncuestadoForm(request.POST)
        if form.is_valid():
            encuestado = form.save(commit=False)
            encuestado.save()
            
            # Registrar creación de encuestado en bitácora
            registrar_bitacora(
                accion='crear',
                tipo_objeto='encuestado',
                descripcion=f'Se creó el encuestado "{encuestado.nombre} {encuestado.apellido}"',
                objeto_id=encuestado.id,
                objeto_nombre=f'{encuestado.nombre} {encuestado.apellido}',
                request=request
            )
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'encuestado': {
                        'id': encuestado.id,
                        'nombre': encuestado.nombre,
                        'apellido': encuestado.apellido,
                        'cedula_completa': f"{encuestado.tipo_cedula}-{encuestado.cedula_numero}",
                        'genero': encuestado.get_genero_display(),
                        'telefono': encuestado.telefono or '',
                        'direccion': encuestado.direccion or '',
                        'cargo': encuestado.cargo or '',
                        'ubicacion_administrativa': encuestado.ubicacion_administrativa or '',
                        'fecha_registro': encuestado.fecha_registro.strftime('%d/%m/%Y %H:%M'),
                    }
                })
            
            messages.success(request, "Encuestado creado correctamente.")
            return redirect('listar_encuestados')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return redirect('listar_encuestados')

def verificar_cedula(request):
    cedula = request.GET.get('cedula_numero', None)
    if not cedula:
        return JsonResponse({'existe': False})
    
    existe = Encuestado.objects.filter(cedula_numero=cedula, papelera=False).exists()
    return JsonResponse({'existe': existe})

@csrf_exempt
@require_POST
@login_required
def editar_encuestado(request, pk):
    encuestado = get_object_or_404(Encuestado, pk=pk)
    
    # Obtener datos del POST
    encuestado.nombre = request.POST.get('nombre')
    encuestado.apellido = request.POST.get('apellido')
    encuestado.tipo_cedula = request.POST.get('tipo_cedula')
    encuestado.cedula_numero = request.POST.get('cedula_numero')
    encuestado.genero = request.POST.get('genero')
    
    # Campos opcionales
    telefono_prefijo = request.POST.get('telefono_prefijo', '')
    telefono_numero = request.POST.get('telefono_numero', '')
    if telefono_prefijo and telefono_numero:
        encuestado.telefono = telefono_prefijo + telefono_numero
    else:
        encuestado.telefono = ''
    
    encuestado.direccion = request.POST.get('direccion', '')
    encuestado.cargo = request.POST.get('cargo', '')
    encuestado.ubicacion_administrativa = request.POST.get('ubicacion_administrativa', '')
    
    encuestado.save()
    
    # Registrar edición de encuestado en bitácora
    registrar_bitacora(
        accion='editar',
        tipo_objeto='encuestado',
        descripcion=f'Se editó el encuestado "{encuestado.nombre} {encuestado.apellido}"',
        objeto_id=encuestado.id,
        objeto_nombre=f'{encuestado.nombre} {encuestado.apellido}',
        request=request
    )
    
    return JsonResponse({
        'success': True,
        'encuestado': {
            'id': encuestado.id,
            'nombre': encuestado.nombre,
            'apellido': encuestado.apellido,
            'cedula_completa': f"{encuestado.tipo_cedula}-{encuestado.cedula_numero}",
        }
    })

@login_required
def restaurar_encuestado(request, encuestado_id):
    encuestado = get_object_or_404(Encuestado, id=encuestado_id)
    encuestado.papelera = False
    encuestado.save()
    
    # Registrar restauración de encuestado en bitácora
    registrar_bitacora(
        accion='restaurar',
        tipo_objeto='encuestado',
        descripcion=f'Se restauró el encuestado "{encuestado.nombre} {encuestado.apellido}" desde la papelera',
        objeto_id=encuestado.id,
        objeto_nombre=f'{encuestado.nombre} {encuestado.apellido}',
        request=request
    )
    
    messages.success(request, "Encuestado restaurado correctamente.")
    return redirect('papelera')

@login_required
def eliminar_encuestado(request, encuestado_id):
    encuestado = get_object_or_404(Encuestado, id=encuestado_id)
    
    # Debug: verificar si el encuestado está en papelera
    if not encuestado.papelera:
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({
                'success': False,
                'message': 'Error: El encuestado no está en la papelera.'
            })
        messages.error(request, "Error: El encuestado no está en la papelera.")
        return redirect('papelera')
    
    if request.method == 'POST':
        # Verificar contraseña del super usuario
        password = request.POST.get('password')
        superuser = User.objects.filter(is_superuser=True).first()
        if not password or not superuser or not superuser.check_password(password):
            # Retornar JSON para AJAX
            if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and 'application/json' in request.headers.get('Accept', ''):
                return JsonResponse({
                    'success': False,
                    'message': 'Contraseña de super usuario incorrecta.'
                })
            
            messages.error(request, "Contraseña de super usuario incorrecta.")
            return redirect('papelera')
        
        nombre_completo = f'{encuestado.nombre} {encuestado.apellido}'
        encuestado.delete()
        
        # Registrar eliminación permanente de encuestado en bitácora
        registrar_bitacora(
            accion='eliminar',
            tipo_objeto='encuestado',
            descripcion=f'Se eliminó permanentemente el encuestado "{nombre_completo}"',
            objeto_id=encuestado_id,
            objeto_nombre=nombre_completo,
            request=request
        )
        
        # Retornar JSON para AJAX
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({
                'success': True,
                'message': f'Encuestado "{nombre_completo}" eliminado correctamente.'
            })
        
        messages.success(request, "Encuestado eliminado correctamente.")
        return redirect('papelera')
    return redirect('papelera')

@login_required
@require_POST
def enviar_a_papelera_encuestado(request, encuestado_id):
    encuestado = get_object_or_404(Encuestado, id=encuestado_id)
    encuestado.papelera = True
    encuestado.save()
    
    # Registrar envío a papelera de encuestado en bitácora
    registrar_bitacora(
        accion='eliminar',
        tipo_objeto='encuestado',
        descripcion=f'Se envió a papelera el encuestado "{encuestado.nombre} {encuestado.apellido}"',
        objeto_id=encuestado.id,
        objeto_nombre=f'{encuestado.nombre} {encuestado.apellido}',
        request=request
    )
    
    return JsonResponse({'success': True})

# ----------------- VISTAS DE ENCUESTAS -----------------

def listar_encuestas(request):
    encuestas = Encuesta.objects.filter(papelera=False)
    today = date.today()
    # Convertir fecha_finalizacion a date para cada encuesta
    for encuesta in encuestas:
        if encuesta.fecha_finalizacion:
            encuesta.fecha_finalizacion_date = encuesta.fecha_finalizacion
        else:
            encuesta.fecha_finalizacion_date = None
    return render(request, 'encuestas/listar.html', {
        'encuestas': encuestas,
        'today': today,
    })

@login_required
def crear_encuesta(request):
    if request.method == 'POST':
        data = request.POST.copy()
        fecha = data.get('fecha_finalizacion')
        # Normaliza fecha si viene como dd/mm/yyyy
        if fecha and '/' in fecha:
            try:
                d, m, y = fecha.split('/')
                data['fecha_finalizacion'] = f"{y}-{m}-{d}"
            except Exception:
                pass  # Si falla, deja el valor original

        form = EncuestaForm(data)
        if form.is_valid():
            encuesta = form.save(commit=False)
            encuesta.usuario = request.user
            encuesta.save()
            
            # Registrar creación de encuesta en bitácora
            registrar_bitacora(
                accion='crear',
                tipo_objeto='encuesta',
                descripcion=f'Se creó la encuesta "{encuesta.titulo}"',
                objeto_id=encuesta.id,
                objeto_nombre=encuesta.titulo,
                request=request
            )
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': "Encuesta creada correctamente.",
                    'encuesta': {
                        'id': encuesta.id,
                        'titulo': encuesta.titulo,
                        'descripcion': encuesta.descripcion,
                        'fecha_finalizacion': encuesta.fecha_finalizacion.strftime('%Y-%m-%d') if encuesta.fecha_finalizacion else '',
                    }
                })
            messages.success(request, "Encuesta creada correctamente.")
            return redirect('listar_encuestas')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = EncuestaForm()
    return render(request, 'encuestas/crear.html', {'form': form})

@login_required
def editar_encuesta(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, id=encuesta_id)
    if request.method == 'POST':
        form = EncuestaForm(request.POST, instance=encuesta)
        if form.is_valid():
            encuesta = form.save()
            
            # Registrar edición de encuesta en bitácora
            registrar_bitacora(
                accion='editar',
                tipo_objeto='encuesta',
                descripcion=f'Se editó la encuesta "{encuesta.titulo}"',
                objeto_id=encuesta.id,
                objeto_nombre=encuesta.titulo,
                request=request
            )
            
            # Soporte para AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': "Encuesta actualizada correctamente.",
                    'encuesta': {
                        'id': encuesta.id,
                        'titulo': encuesta.titulo,
                        'descripcion': encuesta.descripcion,
                        'fecha_finalizacion': encuesta.fecha_finalizacion.strftime('%Y-%m-%d') if encuesta.fecha_finalizacion else '',
                    }
                })
            messages.success(request, "Encuesta actualizada correctamente.")
            return redirect('listar_encuestas')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = EncuestaForm(instance=encuesta)
    return render(request, 'encuestas/crear.html', {
        'form': form,
        'editar': True,
        'encuesta': encuesta
    })

@login_required
def detalle_encuesta(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)
    preguntas = encuesta.items.all()  # ItemEncuesta
    detalles = Respuesta.objects.filter(encuesta=encuesta)
    today = date.today()
    # Convertir fecha_finalizacion a date si existe
    if encuesta.fecha_finalizacion:
        encuesta.fecha_finalizacion_date = encuesta.fecha_finalizacion
    else:
        encuesta.fecha_finalizacion_date = None
    return render(request, 'encuestas/detalle_encuesta.html', {
        'encuesta': encuesta,
        'preguntas': preguntas,
        'detalles': detalles,
        'today': today,
    })

@login_required
@require_POST
def desactivar_encuesta(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, id=encuesta_id)
    encuesta.fecha_finalizacion = date.today()
    encuesta.save()
    
    # Registrar desactivación de encuesta en bitácora
    registrar_bitacora(
        accion='desactivar',
        tipo_objeto='encuesta',
        descripcion=f'Se desactivó la encuesta "{encuesta.titulo}"',
        objeto_id=encuesta.id,
        objeto_nombre=encuesta.titulo,
        request=request
    )
    
    return redirect('listar_encuestas')

@login_required
def reabrir_encuesta(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, id=encuesta_id)
    if request.method == 'POST':
        password = request.POST.get('password')
        nueva_fecha = request.POST.get('nueva_fecha_finalizacion')
        user = authenticate(request, username=request.user.username, password=password)
        if user is not None and request.user.is_superuser:
            if not nueva_fecha:
                messages.error(request, 'Debes ingresar una nueva fecha de finalización.')
                return redirect(f"{reverse('listar_encuestas')}?abrir_modal_reabrir={encuesta.id}")
            encuesta.fecha_finalizacion = nueva_fecha
            encuesta.save()
            
            # Registrar reapertura de encuesta en bitácora
            registrar_bitacora(
                accion='reabrir',
                tipo_objeto='encuesta',
                descripcion=f'Se reabrió la encuesta "{encuesta.titulo}" con nueva fecha: {nueva_fecha}',
                objeto_id=encuesta.id,
                objeto_nombre=encuesta.titulo,
                request=request
            )
            
            messages.success(request, 'La encuesta ha sido reabierta y la fecha de finalización actualizada.')
            return redirect('listar_encuestas')
        else:
            messages.error(request, 'Contraseña incorrecta o no tienes permisos para reabrir encuestas.')
            return redirect(f"{reverse('listar_encuestas')}?abrir_modal_reabrir={encuesta.id}")
    return redirect('listar_encuestas')



# ----------------- PAPELERA -----------------
@login_required
@require_POST
def enviar_a_papelera_encuesta(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, id=encuesta_id)
    encuesta.papelera = True
    encuesta.save()
    
    # Registrar envío a papelera en bitácora
    registrar_bitacora(
        accion='eliminar',
        tipo_objeto='encuesta',
        descripcion=f'Se envió a papelera la encuesta "{encuesta.titulo}"',
        objeto_id=encuesta.id,
        objeto_nombre=encuesta.titulo,
        request=request
    )
    
    return JsonResponse({
        'success': True, 
        'message': f'Encuesta "{encuesta.titulo}" enviada a papelera correctamente',
        'encuesta_id': encuesta.id
    })

@login_required
def restaurar_encuesta(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, id=encuesta_id)
    encuesta.papelera = False
    encuesta.save()
    
    # Registrar restauración en bitácora
    registrar_bitacora(
        accion='restaurar',
        tipo_objeto='encuesta',
        descripcion=f'Se restauró la encuesta "{encuesta.titulo}" desde la papelera',
        objeto_id=encuesta.id,
        objeto_nombre=encuesta.titulo,
        request=request
    )
    
    return redirect('listar_papelera')

@login_required
def eliminar_encuesta(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, id=encuesta_id)
    
    # Debug: verificar si la encuesta está en papelera
    if not encuesta.papelera:
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({
                'success': False,
                'message': 'Error: La encuesta no está en la papelera.'
            })
        messages.error(request, "Error: La encuesta no está en la papelera.")
        return redirect('papelera')
    
    if request.method == 'POST':
        # Verificar contraseña del super usuario
        password = request.POST.get('password')
        superuser = User.objects.filter(is_superuser=True).first()
        if not password or not superuser or not superuser.check_password(password):
            # Retornar JSON para AJAX
            if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and 'application/json' in request.headers.get('Accept', ''):
                return JsonResponse({
                    'success': False,
                    'message': 'Contraseña de super usuario incorrecta.'
                })
            
            messages.error(request, "Contraseña de super usuario incorrecta.")
            return redirect('papelera')
        
        titulo_encuesta = encuesta.titulo
        encuesta.delete()
        
        # Registrar eliminación permanente en bitácora
        registrar_bitacora(
            accion='eliminar',
            tipo_objeto='encuesta',
            descripcion=f'Se eliminó permanentemente la encuesta "{titulo_encuesta}"',
            objeto_id=encuesta_id,
            objeto_nombre=titulo_encuesta,
            request=request
        )
        
        # Retornar JSON para AJAX
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({
                'success': True,
                'message': f'Encuesta "{titulo_encuesta}" eliminada correctamente.'
            })
        
        return redirect('listar_papelera')
    return render(request, 'encuestas/eliminar.html', {'encuesta': encuesta})

# ----------------- PREGUNTAS (ItemEncuesta) -----------------

@require_POST
@login_required
def agregar_pregunta(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)
    texto_pregunta = request.POST.get('texto_pregunta', '').strip()
    if not texto_pregunta:
        return JsonResponse({'ok': False, 'error': 'La pregunta no puede estar vacía.'}, status=400)
    tipo_respuesta = request.POST.get('tipo_respuesta')
    opciones = request.POST.getlist('opciones[]')
    tipo_pregunta = tipo_respuesta if tipo_respuesta in dict(ItemEncuesta.TIPO_PREGUNTA_CHOICES) else 'texto'
    orden = encuesta.items.count() + 1

    # Obtener el título del campo de texto adicional si existe
    titulo_campo_texto = None
    if tipo_respuesta == 'si_no' and request.POST.get('requiere_campo_texto') == 'on':
        titulo_campo_texto = request.POST.get('titulo_campo_texto', '').strip()
        if not titulo_campo_texto:
            titulo_campo_texto = 'Indique cuál'
    
    pregunta = ItemEncuesta.objects.create(
        texto_pregunta=texto_pregunta,
        tipo_pregunta=tipo_pregunta,
        encuesta=encuesta,
        tipo_respuesta=tipo_respuesta,
        orden=orden,
        requerida=False,
        titulo_campo_texto=titulo_campo_texto
    )

    # Si es una pregunta de opción única o múltiple, se crean las opciones
    if tipo_respuesta in ['opcion_unica', 'opcion_multiple']:
        for opcion_texto in opciones:
            if opcion_texto.strip():
                OpcionPregunta.objects.create(item_encuesta=pregunta, texto_opcion=opcion_texto)

    # Registrar creación de pregunta en bitácora
    registrar_bitacora(
        accion='crear',
        tipo_objeto='pregunta',
        descripcion=f'Se agregó la pregunta "{texto_pregunta[:50]}..." a la encuesta "{encuesta.titulo}"',
        objeto_id=pregunta.id,
        objeto_nombre=texto_pregunta[:50],
        request=request
    )

    return JsonResponse({'ok': True, 'pregunta_id': pregunta.id})

@login_required
def obtener_pregunta(request):
    pregunta_id = request.GET.get('pregunta_id')
    pregunta = get_object_or_404(ItemEncuesta, pk=pregunta_id)
    opciones = list(pregunta.opciones.values('id', 'texto_opcion'))
    return JsonResponse({
        'id': pregunta.id,
        'texto_pregunta': pregunta.texto_pregunta,
        'tipo_respuesta': pregunta.tipo_respuesta,
        'opciones': opciones,
        'titulo_campo_texto': pregunta.titulo_campo_texto
    })

@csrf_exempt
@require_POST
@login_required
def editar_pregunta_ajax(request):

    pregunta_id = request.POST.get('pregunta_id')
    texto_pregunta = request.POST.get('texto_pregunta')
    tipo_respuesta = request.POST.get('tipo_respuesta')
    opciones = request.POST.getlist('opciones[]')
    pregunta = get_object_or_404(ItemEncuesta, pk=pregunta_id)
    pregunta.texto_pregunta = texto_pregunta
    pregunta.tipo_respuesta = tipo_respuesta
    
    # Actualizar el título del campo de texto adicional
    if tipo_respuesta == 'si_no' and request.POST.get('requiere_campo_texto') == 'on':
        titulo_campo_texto = request.POST.get('titulo_campo_texto', '').strip()
        pregunta.titulo_campo_texto = titulo_campo_texto if titulo_campo_texto else 'Indique cuál'
    else:
        pregunta.titulo_campo_texto = None
    
    pregunta.save()
    # Actualizar opciones
    if tipo_respuesta in ['opcion_unica', 'opcion_multiple']:
        pregunta.opciones.all().delete()
        for opcion_texto in opciones:
            if opcion_texto.strip():
                OpcionPregunta.objects.create(item_encuesta=pregunta, texto_opcion=opcion_texto)
    else:
        pregunta.opciones.all().delete()
    
    # Registrar edición de pregunta en bitácora
    registrar_bitacora(
        accion='editar',
        tipo_objeto='pregunta',
        descripcion=f'Se editó la pregunta "{texto_pregunta[:50]}..." en la encuesta "{pregunta.encuesta.titulo}"',
        objeto_id=pregunta.id,
        objeto_nombre=texto_pregunta[:50],
        request=request
    )
    
    return JsonResponse({'ok': True})

@require_POST
def eliminar_pregunta(request):
    pregunta_id = request.POST.get('pregunta_id')
    try:
        pregunta = ItemEncuesta.objects.get(id=pregunta_id)
        texto_pregunta = pregunta.texto_pregunta
        encuesta_titulo = pregunta.encuesta.titulo
        pregunta.delete()
        
        # Registrar eliminación de pregunta en bitácora
        registrar_bitacora(
            accion='eliminar',
            tipo_objeto='pregunta',
            descripcion=f'Se eliminó la pregunta "{texto_pregunta[:50]}..." de la encuesta "{encuesta_titulo}"',
            objeto_id=pregunta_id,
            objeto_nombre=texto_pregunta[:50],
            request=request
        )
        
        return JsonResponse({'ok': True})
    except ItemEncuesta.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Pregunta no encontrada'})
    

@login_required
def detalles_pregunta(request):
    pregunta_id = request.GET.get('pregunta_id')
    pregunta = get_object_or_404(ItemEncuesta, pk=pregunta_id)
    opciones = []
    labels = []
    values = []
    if pregunta.tipo_respuesta in ['opcion_unica', 'opcion_multiple']:
        for opcion in pregunta.opciones.all():
            cantidad = opcion.respuestas_opcion.count()  # <-- Este related_name debe existir
            opciones.append({'texto_opcion': opcion.texto_opcion, 'cantidad': cantidad})
            labels.append(opcion.texto_opcion)
            values.append(cantidad)
    elif pregunta.tipo_respuesta == 'si_no':
        cantidad_si = pregunta.respuestas.filter(valor_respuesta__iexact='Sí').count()
        cantidad_no = pregunta.respuestas.filter(valor_respuesta__iexact='No').count()
        opciones = [
            {'texto_opcion': 'Sí', 'cantidad': cantidad_si},
            {'texto_opcion': 'No', 'cantidad': cantidad_no},
        ]
        labels = ['Sí', 'No']
        values = [cantidad_si, cantidad_no]
        print('SI:', cantidad_si, 'NO:', cantidad_no)
    else:
        opciones = []
    return JsonResponse({
        'texto_pregunta': pregunta.texto_pregunta,
        'opciones': opciones,
        'labels': labels,
        'values': values
    })


# ----------------- RESPUESTAS (ItemRespuesta) -----------------

@login_required
def agregar_respuesta(request, item_encuesta_id):
    item_encuesta = get_object_or_404(ItemEncuesta, pk=item_encuesta_id)
    if request.method == 'POST':
        form = ItemRespuestaForm(request.POST)
        if form.is_valid():
            respuesta = form.save(commit=False)
            respuesta.item_encuesta = item_encuesta
            respuesta.save()
            messages.success(request, "Respuesta agregada correctamente.")
            return redirect('detalle_encuesta', encuesta_id=item_encuesta.encuesta.id)
    else:
        form = ItemRespuestaForm()
    return render(request, 'encuestas/agregar_respuesta.html', {'form': form, 'item_encuesta': item_encuesta})

# ----------------- RESPONDER ENCUESTA (USUARIO) -----------------

@login_required
def responder_encuesta(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)
    preguntas = encuesta.items.all()
    encuestado = Encuestado.objects.get(usuario=request.user)
    if request.method == 'POST':
        # Crea la respuesta principal
        respuesta = Respuesta.objects.create(
            encuesta=encuesta,
            encuestado=encuestado,
            usuario=request.user
        )
        for pregunta in preguntas:
            respuesta_texto = request.POST.get(f'pregunta_{pregunta.id}')
            if respuesta_texto:
                ItemRespuesta.objects.create(
                    item_encuesta=pregunta,
                    encuestado=encuestado,
                    respuesta=respuesta,
                    texto_respuesta=respuesta_texto
                )
        
        # Registrar envío de respuestas en bitácora
        registrar_bitacora(
            accion='enviar',
            tipo_objeto='respuesta',
            descripcion=f'Se enviaron respuestas para la encuesta "{encuesta.titulo}" por el encuestado "{encuestado.nombre} {encuestado.apellido}"',
            objeto_id=respuesta.id,
            objeto_nombre=f'Respuesta {respuesta.id}',
            request=request
        )
        
        messages.success(request, "Respuestas enviadas correctamente.")
        return redirect('detalle_respuesta', respuesta_id=respuesta.id)
    return render(request, 'encuestas/responder.html', {'encuesta': encuesta, 'preguntas': preguntas})


# ----------------- SELECCIONAR ENCUESTA PARA ENCUESTADO -----------------

@login_required
def seleccionar_encuesta_encuestado(request):
    encuestados = Encuestado.objects.all()
    today = date.today()
    
    # Esta consulta inicial es eficiente y está muy bien planteada.
    encuestas = Encuesta.objects.filter(
        activo=True,
        papelera=False
    ).filter(
        Q(fecha_finalizacion__isnull=True) | Q(fecha_finalizacion__gt=today)
    ).annotate(
        pregunta_count=Count('items')
    ).filter(
        pregunta_count__gt=0
    ).order_by('titulo')
    
    error = None

    if request.method == "POST":
        encuestado_id = request.POST.get("encuestado")
        encuesta_id = request.POST.get("encuesta")
        
        # 1. Validación inicial: Asegurarse de que se enviaron ambos IDs.
        if not encuestado_id or not encuesta_id:
            error = "Debes seleccionar una encuesta y un encuestado."
        else:
            # 2. Se combinan todas las validaciones de la encuesta en una sola consulta.
            #    Si la encuesta no cumple ALGUNA condición, simplemente no se encontrará.
            try:
                encuesta_valida = Encuesta.objects.get(
                    id=encuesta_id,
                    activo=True,
                    papelera=False
                )
                
                # Verificar que la encuesta no esté finalizada
                if encuesta_valida.fecha_finalizacion and encuesta_valida.fecha_finalizacion <= today:
                    error = "Esta encuesta ya ha finalizado."
                else:
                    # 3. Validar que el encuestado existe.
                    if not Encuestado.objects.filter(id=encuestado_id).exists():
                        error = "El encuestado seleccionado no es válido."
                    # 4. Validar que la encuesta tiene preguntas (se puede hacer después del get).
                    elif not encuesta_valida.items.exists():
                        error = "Esta encuesta no tiene preguntas asignadas."
                    # 5. Validar si ya existe una respuesta (la lógica original estaba bien).
                    elif Respuesta.objects.filter(encuestado_id=encuestado_id, encuesta_id=encuesta_id, papelera=False).exists():
                        error = "Este encuestado ya respondió esa encuesta."
                    else:
                        # Si todo es correcto, redirigir.
                        return redirect('realizar_encuesta', encuesta_id=encuesta_id, encuestado_id=encuestado_id)
            except Encuesta.DoesNotExist:
                # Este error ahora significa que la encuesta no existe O no está activa, o ya finalizó.
                error = "La encuesta seleccionada no es válida o ya no está disponible."

    return render(request, "encuestas/seleccionar_encuesta.html", {
        "encuestados": encuestados,
        "encuestas": encuestas,
        "error": error,
    })

@login_required
def realizar_encuesta(request, encuesta_id, encuestado_id):
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)
    encuestado = get_object_or_404(Encuestado, pk=encuestado_id)
    preguntas = encuesta.items.all().order_by('orden')
    
    # Validaciones previas antes de mostrar la encuesta
    today = date.today()
    
    # Verificar que la encuesta esté activa
    if not encuesta.activo:
        messages.error(request, "Esta encuesta no está activa.")
        return redirect('seleccionar_encuesta_encuestado')
    
    # Verificar que la encuesta no esté finalizada
    if encuesta.fecha_finalizacion and encuesta.fecha_finalizacion <= today:
        messages.error(request, "Esta encuesta ya ha finalizado.")
        return redirect('seleccionar_encuesta_encuestado')
    
    # Verificar que la encuesta tenga preguntas
    if not preguntas.exists():
        messages.error(request, "Esta encuesta no tiene preguntas asignadas.")
        return redirect('seleccionar_encuesta_encuestado')
    
    # Verificar si ya existe una respuesta (para permitir edición)
    respuesta_existente = Respuesta.objects.filter(encuestado=encuestado, encuesta=encuesta, papelera=False).first()
    es_edicion = respuesta_existente is not None
    
    # Si no es edición y ya existe respuesta, mostrar error
    if not es_edicion and Respuesta.objects.filter(encuestado=encuestado, encuesta=encuesta, papelera=False).exists():
        messages.error(request, "Este encuestado ya respondió esta encuesta.")
        return redirect('seleccionar_encuesta_encuestado')

    if request.method == "POST":
        errores = []
        # Validación de preguntas requeridas
        for pregunta in preguntas:
            nombre_campo = f"pregunta_{pregunta.id}"
            if pregunta.requerida:
                if pregunta.tipo_respuesta == 'opcion_multiple':
                    valores = request.POST.getlist(nombre_campo)
                    if not valores:
                        errores.append(f"La pregunta '{pregunta.texto_pregunta}' es obligatoria.")
                else:
                    valor = request.POST.get(nombre_campo)
                    if not valor:
                        errores.append(f"La pregunta '{pregunta.texto_pregunta}' es obligatoria.")

        # Validación de contraseña de superusuario
        password = request.POST.get('superuser_password')
        superuser = None
        if password:
            superuser = User.objects.filter(is_superuser=True, is_active=True).first()
            if not superuser or not superuser.check_password(password):
                errores.append("Contraseña de superusuario incorrecta.")
        else:
            errores.append("Debes ingresar la contraseña de superusuario.")

        if errores:
            from django.contrib import messages
            for error in errores:
                messages.error(request, error)
            return render(request, "encuestas/realizar_encuesta.html", {
                "encuesta": encuesta,
                "encuestado": encuestado,
                "preguntas": preguntas,
                "es_edicion": es_edicion,
                "respuesta_existente": respuesta_existente,
            })

        # Si es edición, actualizar la respuesta existente; si no, crear una nueva
        if es_edicion:
            respuesta = respuesta_existente
            respuesta.ultima_actualizacion = timezone.now()
            respuesta.save()
            # Eliminar respuestas anteriores
            respuesta.items_respuesta.all().delete()
        else:
            respuesta = Respuesta.objects.create(
                encuesta=encuesta,
                encuestado=encuestado,
                usuario=request.user,
            )

        for pregunta in preguntas:
            nombre_campo = f"pregunta_{pregunta.id}"
            if pregunta.tipo_respuesta == 'opcion_multiple':
                valores = request.POST.getlist(nombre_campo)
                for valor in valores:
                    opcion = OpcionPregunta.objects.filter(pk=valor).first()
                    ItemRespuesta.objects.create(
                        item_encuesta=pregunta,
                        encuestado=encuestado,
                        respuesta=respuesta,
                        opcion=opcion,
                        valor_respuesta=valor
                    )
            elif pregunta.tipo_respuesta == 'opcion_unica':
                valor = request.POST.get(nombre_campo)
                opcion = OpcionPregunta.objects.filter(pk=valor).first()
                ItemRespuesta.objects.create(
                    item_encuesta=pregunta,
                    encuestado=encuestado,
                    respuesta=respuesta,
                    opcion=opcion,
                    valor_respuesta=valor
                )
            elif pregunta.tipo_respuesta == 'si_no':
                valor = request.POST.get(nombre_campo)
                campo_texto_adicional = ""
                # Si la pregunta tiene campo de texto adicional y el usuario respondió "Sí"
                if pregunta.titulo_campo_texto and valor == "Sí":
                    campo_texto_adicional = request.POST.get(f"campo_texto_{pregunta.id}", "")
                ItemRespuesta.objects.create(
                    item_encuesta=pregunta,
                    encuestado=encuestado,
                    respuesta=respuesta,
                    texto_respuesta=campo_texto_adicional,
                    valor_respuesta=valor
                )
            else:
                valor = request.POST.get(nombre_campo)
                ItemRespuesta.objects.create(
                    item_encuesta=pregunta,
                    encuestado=encuestado,
                    respuesta=respuesta,
                    texto_respuesta=valor if pregunta.tipo_respuesta == 'texto' else "",
                    valor_respuesta=valor
                )
        # Mensaje de éxito antes de redirigir
        from django.contrib import messages
        if es_edicion:
            messages.success(request, "¡Respuestas actualizadas correctamente!")
        else:
            messages.success(request, "¡Respuestas enviadas correctamente!")
        return redirect('detalle_respuesta', respuesta_id=respuesta.id)

    # Cargar respuestas existentes si es edición
    respuestas_existentes = {}
    if es_edicion and respuesta_existente:
        for item in respuesta_existente.items_respuesta.all():
            pregunta_id = item.item_encuesta.id
            if pregunta_id not in respuestas_existentes:
                respuestas_existentes[pregunta_id] = []
            
            if item.opcion:
                respuestas_existentes[pregunta_id].append(str(item.opcion.id))
            elif item.valor_respuesta:
                respuestas_existentes[pregunta_id].append(item.valor_respuesta)
            elif item.texto_respuesta:
                respuestas_existentes[pregunta_id].append(item.texto_respuesta)

    return render(request, "encuestas/realizar_encuesta.html", {
        "encuesta": encuesta,
        "encuestado": encuestado,
        "preguntas": preguntas,
        "es_edicion": es_edicion,
        "respuesta_existente": respuesta_existente,
        "respuestas_existentes": respuestas_existentes,
    })


# ----------------- Lista de reportes de encuesta -----------------


@login_required
def reportes_respondientes(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, id=encuesta_id)
    respuestas = Respuesta.objects.filter(encuesta=encuesta, papelera=False).select_related('encuestado')
    return render(request, "encuestas/listar_respondientes.html", {
        "encuesta": encuesta,
        "respuestas": respuestas
    })

@login_required
def listar_reportes(request):
    encuestas = Encuesta.objects.filter(papelera=False)
    today = date.today()
    return render(request, "encuestas/listar_reportes.html", {
        "encuestas": encuestas,
        "today": today
    })

@login_required
def detalle_respuesta(request, respuesta_id):
    respuesta = get_object_or_404(Respuesta, id=respuesta_id)
    items_respuesta = respuesta.items_respuesta.select_related('item_encuesta', 'opcion').all()

    agrupadas = OrderedDict()
    for item in items_respuesta:
        pregunta = item.item_encuesta.texto_pregunta
        if item.opcion:
            texto = item.opcion.texto_opcion
        elif item.texto_respuesta:
            texto = item.texto_respuesta
        elif item.valor_respuesta:
            texto = item.valor_respuesta
        else:
            texto = "Sin respuesta"
        
        # Si es una pregunta Sí/No con campo adicional
        if item.item_encuesta.tipo_respuesta == 'si_no' and item.item_encuesta.titulo_campo_texto:
            if item.valor_respuesta == "Sí" and item.texto_respuesta:
                texto = f"{item.valor_respuesta} - {item.item_encuesta.titulo_campo_texto}: {item.texto_respuesta}"
            else:
                texto = item.valor_respuesta if item.valor_respuesta else "Sin respuesta"
        
        if pregunta not in agrupadas:
            agrupadas[pregunta] = []
        agrupadas[pregunta].append(texto)

    # Si la petición es AJAX, retorna solo el contenido del detalle
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string("encuestas/detalle_respuesta1.html", {
            "respuesta": respuesta,
            "respuestas_agrupadas": agrupadas,
        })
        return HttpResponse(html)
    else:
        return render(request, "encuestas/detalle_respuesta.html", {
            "respuesta": respuesta,
            "respuestas_agrupadas": agrupadas,
        })
# ----------------- PAPELERA -----------------
@login_required
def restaurar_respuesta(request, respuesta_id):
    respuesta = get_object_or_404(Respuesta, id=respuesta_id)
    respuesta.papelera = False
    respuesta.save()
    return redirect('listar_papelera')

@login_required
def enviar_a_papelera(request, respuesta_id):
    respuesta = get_object_or_404(Respuesta, id=respuesta_id)
    respuesta.papelera = True
    respuesta.save()
    return redirect('listar_reportes')

@login_required
def eliminar_respuesta(request, respuesta_id):
    respuesta = get_object_or_404(Respuesta, id=respuesta_id)
    respuesta.delete()
    return redirect('listar_papelera')

@login_required
def papelera(request):
    encuestas = Encuesta.objects.filter(papelera=True)
    respuestas = Respuesta.objects.filter(papelera=True)
    encuestados = Encuestado.objects.filter(papelera=True)
    return render(request, 'papelera.html', {
        'encuestas': encuestas,
        'respuestas': respuestas,
        'encuestados': encuestados,
    })

from socket import gaierror

def password_reset_confirm(request, uidb64=None, token=None):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        user = User.objects.filter(email=email).first()
        form = CustomSetPasswordForm(user, request.POST or None)
        if user and not user.is_active:
            messages.error(request, 'Tu usuario está bloqueado. Contacta al superadministrador.')
            return render(request, 'registration/password_reset_1.html', {'form': form})
        try:
            if form.is_valid():
                form.save(
                    request=request,
                    use_https=request.is_secure(),
                    email_template_name='registration/password_reset_email.html'
                )
                messages.success(request, 'Si el correo existe y está habilitado, recibirás instrucciones para recuperar tu contraseña.')
                return redirect('password_reset_done')
        except gaierror:
            # Error de conexión a internet
            return render(request, 'registration/no_internet.html')
    else:
        form = PasswordResetForm()
    return render(request, 'registration/password_reset_1.html', {'form': form})

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        email = request.POST.get('email', '').strip()
        user_exists = User.objects.filter(email=email).exists()
        email = request.POST.get('email', '').strip()
        user_exists = User.objects.filter(email=email).exists()
        if not user_exists:
            messages.error(request, 'El correo no está registrado.')
            return render(request, 'registration/password_reset_1.html', {'form': form})
        if form.is_valid():
            try:
                form.save(
                    request=request,
                    use_https=request.is_secure(),
                    email_template_name='registration/password_reset_email.html'
                )
                messages.success(request, 'Si el correo existe y está habilitado, recibirás instrucciones para recuperar tu contraseña.')
                return redirect('password_reset_done')
            except gaierror:
                # Error de conexión a internet
                return render(request, 'registration/no_internet1.html')
    else:
        form = PasswordResetForm()
    return render(request, 'registration/password_reset_1.html', {'form': form})



@login_required
def generar_pdf_encuestas(request):
    """
    Vista para generar PDF con múltiples encuestas
    Permite seleccionar encuestas específicas o todas
    """
    if request.method == 'POST':
        encuesta_ids = request.POST.getlist('encuesta_ids')
        
        if encuesta_ids:
            # Encuestas específicas seleccionadas
            encuestas = Encuesta.objects.filter(
                id__in=encuesta_ids, 
                papelera=False
            ).order_by('fecha_creacion')
        else:
            # Todas las encuestas activas
            encuestas = Encuesta.objects.filter(papelera=False).order_by('fecha_creacion')
        
        if not encuestas.exists():
            messages.error(request, 'No hay encuestas disponibles para generar el PDF.')
            return redirect('listar_encuestas')
        
        # Preparar encuestas con sus estadísticas
        encuestas_con_estadisticas = []
        for encuesta in encuestas:
            preguntas = encuesta.items.all()
            estadisticas = {
                'total_preguntas': preguntas.count(),
                'si_no': preguntas.filter(tipo_respuesta='si_no').count(),
                'opcion_unica': preguntas.filter(tipo_respuesta='opcion_unica').count(),
                'opcion_multiple': preguntas.filter(tipo_respuesta='opcion_multiple').count(),
                'con_campo_texto': preguntas.filter(titulo_campo_texto__isnull=False).exclude(titulo_campo_texto='').count(),
            }
            encuesta.estadisticas = estadisticas
            encuestas_con_estadisticas.append(encuesta)
        
        # Usar ReportLab para generar PDF con logos (igual que encuesta_pdf)
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.lib.colors import black
        import os
        from django.conf import settings
        
        # Crear respuesta HTTP para el PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="encuestas_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf"'
        
        # Crear documento PDF con márgenes reducidos
        doc = SimpleDocTemplate(response, pagesize=A4, 
                              rightMargin=36, leftMargin=36, 
                              topMargin=20, bottomMargin=18)
        
        # Estilos (iguales que encuesta_pdf)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=black
        )
        
        question_style = ParagraphStyle(
            'QuestionStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT,
            textColor=black,
            leftIndent=0
        )
        
        option_style = ParagraphStyle(
            'OptionStyle',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=3,
            alignment=TA_LEFT,
            leftIndent=15,
            textColor=black
        )
        
        line_style = ParagraphStyle(
            'LineStyle',
            parent=styles['Normal'],
            fontSize=8,
            spaceAfter=8,
            alignment=TA_LEFT,
            textColor=black
        )
        
        # Construir contenido del PDF
        story = []
        
        # Procesar cada encuesta
        for encuesta_idx, encuesta in enumerate(encuestas_con_estadisticas):
            # Header con logos solo en la primera página
            if encuesta_idx == 0:
                try:
                    logo_gobernacion_path = os.path.join(settings.MEDIA_ROOT, 'PDF', 'Gobernacion.png')
                    logo_corfalmi_path = os.path.join(settings.MEDIA_ROOT, 'PDF', 'Corfalmi.png')
                    
                    if os.path.exists(logo_gobernacion_path):
                        logo_gobernacion = Image(logo_gobernacion_path, width=1*inch, height=0.5*inch)
                    else:
                        logo_gobernacion = Paragraph("FALCÓN<br/>Gobernación Bolivariana", title_style)
                        
                    if os.path.exists(logo_corfalmi_path):
                        logo_corfalmi = Image(logo_corfalmi_path, width=1*inch, height=0.5*inch)
                    else:
                        logo_corfalmi = Paragraph("CORFALMI<br/>Corporación Falconiana de Minería", title_style)
                    
                    logo_table = Table([[logo_gobernacion, "", logo_corfalmi]], 
                                      colWidths=[3.5*inch, 1*inch, 3.5*inch])
                    logo_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                        ('ALIGN', (2, 0), (2, 0), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ]))
                    
                    story.append(logo_table)
                    story.append(Spacer(1, 8))
                    
                except Exception as e:
                    pass
            
            # Sección de información personal solo en la primera encuesta
            if encuesta_idx == 0:
                info_personal_data = [
                    ["Nombre:", "________________________", "Cédula:", "________________________"],
                    ["Dirección:", "________________________", "Teléfono:", "________________________"]
                ]
                
                info_personal_table = Table(info_personal_data, colWidths=[0.6*inch, 2.3*inch, 1.2*inch, 2.3*inch])
                info_personal_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ]))
                
                story.append(info_personal_table)
                story.append(Spacer(1, 8))
            
            # Solo agregar título para encuestas adicionales (no para la primera)
            if encuesta_idx > 0:
                preguntas_title = Paragraph(f"<b>Encuesta: {encuesta.titulo}</b>", title_style)
                story.append(preguntas_title)
                story.append(Spacer(1, 15))
            
            # Obtener preguntas de esta encuesta
            preguntas = encuesta.items.all().order_by('orden')
            
            # Agregar preguntas de esta encuesta en formato híbrido
            preguntas_por_fila = 3
            preguntas_organizadas = []
            
            for i in range(0, len(preguntas), preguntas_por_fila):
                fila_preguntas = []
                for j in range(preguntas_por_fila):
                    if i + j < len(preguntas):
                        pregunta = preguntas[i + j]
                        
                        # Crear el contenido de la pregunta
                        pregunta_num = i + j + 1
                        pregunta_content = f"{pregunta_num}. {pregunta.texto_pregunta}"
                        
                        # Agregar opciones según el tipo
                        if pregunta.tipo_respuesta == 'si_no':
                            pregunta_content += "\n   ☐ Sí\n   ☐ No"
                            if pregunta.titulo_campo_texto:
                                pregunta_content += f"\n   {pregunta.titulo_campo_texto}: ________________"
                        elif pregunta.tipo_respuesta == 'opcion_unica':
                            for opcion in pregunta.opciones.all():
                                pregunta_content += f"\n   ○ {opcion.texto_opcion}"
                        elif pregunta.tipo_respuesta == 'opcion_multiple':
                            for opcion in pregunta.opciones.all():
                                pregunta_content += f"\n   ☐ {opcion.texto_opcion}"
                        
                        fila_preguntas.append(pregunta_content)
                    else:
                        fila_preguntas.append("")
                
                preguntas_organizadas.append(fila_preguntas)
            
            # Crear tabla con preguntas en 3 columnas
            if preguntas_organizadas:
                preguntas_table = Table(preguntas_organizadas, colWidths=[2.3*inch, 2.3*inch, 2.3*inch])
                preguntas_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ]))
                
                story.append(preguntas_table)
            
            # Duplicar el formulario completo para aprovechar el espacio
            # Agregar separador
            story.append(Spacer(1, 15))
            story.append(Paragraph("_" * 80, line_style))
            story.append(Spacer(1, 10))
            
            # Header duplicado
            try:
                logo_gobernacion_path = os.path.join(settings.MEDIA_ROOT, 'PDF', 'Gobernacion.png')
                logo_corfalmi_path = os.path.join(settings.MEDIA_ROOT, 'PDF', 'Corfalmi.png')
                
                if os.path.exists(logo_gobernacion_path):
                    logo_gobernacion = Image(logo_gobernacion_path, width=1*inch, height=0.5*inch)
                else:
                    logo_gobernacion = Paragraph("FALCÓN<br/>Gobernación Bolivariana", title_style)
                    
                if os.path.exists(logo_corfalmi_path):
                    logo_corfalmi = Image(logo_corfalmi_path, width=1*inch, height=0.5*inch)
                else:
                    logo_corfalmi = Paragraph("CORFALMI<br/>Corporación Falconiana de Minería", title_style)
                
                logo_table2 = Table([[logo_gobernacion, "", logo_corfalmi]], 
                                   colWidths=[3.5*inch, 1*inch, 3.5*inch])
                logo_table2.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('ALIGN', (2, 0), (2, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                
                story.append(logo_table2)
                story.append(Spacer(1, 8))
                
            except Exception as e:
                pass
            
            # Información personal duplicada
            info_personal_data2 = [
                ["Nombre:", "________________________", "Cédula:", "________________________"],
                ["Dirección:", "________________________", "Teléfono:", "________________________"]
            ]
            
            info_personal_table2 = Table(info_personal_data2, colWidths=[0.6*inch, 2.3*inch, 1.2*inch, 2.3*inch])
            info_personal_table2.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ]))
            
            story.append(info_personal_table2)
            story.append(Spacer(1, 8))

            # Preguntas duplicadas
            preguntas_organizadas2 = []
            for i in range(0, len(preguntas), preguntas_por_fila):
                fila_preguntas = []
                for j in range(preguntas_por_fila):
                    if i + j < len(preguntas):
                        pregunta = preguntas[i + j]
                        pregunta_num = i + j + 1
                        pregunta_content = f"{pregunta_num}. {pregunta.texto_pregunta}"
                        
                        if pregunta.tipo_respuesta == 'si_no':
                            pregunta_content += "\n   ☐ Sí\n   ☐ No"
                            if pregunta.titulo_campo_texto:
                                pregunta_content += f"\n   {pregunta.titulo_campo_texto}: ________________"
                        elif pregunta.tipo_respuesta == 'opcion_unica':
                            for opcion in pregunta.opciones.all():
                                pregunta_content += f"\n   ○ {opcion.texto_opcion}"
                        elif pregunta.tipo_respuesta == 'opcion_multiple':
                            for opcion in pregunta.opciones.all():
                                pregunta_content += f"\n   ☐ {opcion.texto_opcion}"
                        
                        fila_preguntas.append(pregunta_content)
                    else:
                        fila_preguntas.append("")
                
                preguntas_organizadas2.append(fila_preguntas)
            
            if preguntas_organizadas2:
                preguntas_table2 = Table(preguntas_organizadas2, colWidths=[2.3*inch, 2.3*inch, 2.3*inch])
                preguntas_table2.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ]))
                
                story.append(preguntas_table2)
            
            # Agregar separador entre encuestas (excepto la última)
            if encuesta_idx < len(encuestas_con_estadisticas) - 1:
                story.append(Spacer(1, 20))
                story.append(Paragraph("_" * 80, line_style))
                story.append(Spacer(1, 15))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("_" * 80, option_style))
        footer_text = f"Sistema de Encuestas - Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        story.append(Paragraph(footer_text, option_style))
        
        # Construir PDF
        doc.build(story)
        
        # Registrar descarga de PDF en bitácora
        registrar_bitacora(
            accion='descargar',
            tipo_objeto='sistema',
            descripcion=f'Se descargó PDF con {len(encuestas)} encuestas seleccionadas',
            objeto_id=None,
            objeto_nombre=f'PDF Encuestas {datetime.now().strftime("%d/%m/%Y")}',
            request=request
        )
        
        return response
    
    # GET request - mostrar formulario de selección
    encuestas = Encuesta.objects.filter(papelera=False).order_by('fecha_creacion')
    return render(request, 'encuestas/seleccionar_pdf.html', {
        'encuestas': encuestas
    })

@login_required
def listar_fotografias(request):
    # Obtener el tipo de filtro desde la URL
    tipo_filtro = request.GET.get('tipo', 'todas')  # 'encuestas', 'comunidades', 'todas'
    
    # Filtrar encuestas que tienen fotografías
    encuestas_con_fotos = []
    if tipo_filtro in ['encuestas', 'todas']:
        encuestas_qs = Encuesta.objects.filter(papelera=False).prefetch_related('fotografias')
        for encuesta in encuestas_qs:
            fotos = encuesta.fotografias.all()
            if fotos.exists():
                encuestas_con_fotos.append({
                    'tipo': 'encuesta',
                    'encuesta': encuesta,
                    'fotos': fotos
                })
    
    # Combinar ambos tipos
    todos_los_grupos = encuestas_con_fotos
    
    return render(request, 'fotografias/listar.html', {
        'encuestas_fotos': encuestas_con_fotos,
        'todos_los_grupos': todos_los_grupos,
        'tipo_filtro': tipo_filtro
    })
@login_required
def ver_fotografia(request, foto_id):
    foto = get_object_or_404(Fotografia, id=foto_id)
    return render(request, 'fotografias/detalle.html', {'foto': foto})

@login_required
def editar_fotografia(request, foto_id):
    foto = get_object_or_404(Fotografia, id=foto_id)
    if request.method == 'POST':
        form = FotografiaForm(request.POST, request.FILES, instance=foto)
        if form.is_valid():
            form.save()
            messages.success(request, 'La fotografía fue editada exitosamente.')
            return redirect('listar_fotografias')
    else:
        form = FotografiaForm(instance=foto)
    return render(request, 'fotografias/editar.html', {'form': form, 'foto': foto})

@login_required
def agregar_foto_encuesta(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)
    if request.method == "POST":
        files = request.FILES.getlist('fotos')
        if not files:
            messages.error(request, "Debes seleccionar al menos una imagen.")
            return redirect('detalle_encuesta', encuesta_id=encuesta.id)
        for f in files:
            foto = Fotografia.objects.create(
                encuesta=encuesta,
                imagen=f,
                subido_por=request.user
            )
            
            # Registrar subida de fotografía en bitácora
            registrar_bitacora(
                accion='subir',
                tipo_objeto='fotografia',
                descripcion=f'Se subió fotografía "{f.name}" a la encuesta "{encuesta.titulo}"',
                objeto_id=foto.id,
                objeto_nombre=f.name,
                request=request
            )
            
        messages.success(request, "¡Fotografía(s) agregada(s) correctamente!")
        return redirect('detalle_encuesta', encuesta_id=encuesta.id)
    return render(request, "fotografias/agregar_foto_encuesta.html", {"encuesta": encuesta})

@login_required
@require_POST
def borrar_fotografia(request, foto_id):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Petición no permitida.'}, status=403)
    foto = get_object_or_404(Fotografia, id=foto_id)
    nombre_foto = foto.imagen.name
    encuesta_titulo = foto.encuesta.titulo
    foto.delete()
    
    # Registrar eliminación de fotografía en bitácora
    registrar_bitacora(
        accion='eliminar',
        tipo_objeto='fotografia',
        descripcion=f'Se eliminó la fotografía "{nombre_foto}" de la encuesta "{encuesta_titulo}"',
        objeto_id=foto_id,
        objeto_nombre=nombre_foto,
        request=request
    )
    
    return JsonResponse({'success': True})

# Vista para encuestas externas
from django.contrib.auth.decorators import login_required



@login_required
@require_POST
def agregar_fotografia_ajax(request):
    try:
        encuesta_id = request.POST.get('encuesta_id')
        tipo = request.POST.get('tipo')
        imagen = request.FILES.get('imagen')
        
        if not imagen:
            return JsonResponse({'success': False, 'error': 'Debe seleccionar una imagen.'})
        
        foto = None
        if tipo == 'encuesta' and encuesta_id:
            encuesta = Encuesta.objects.get(pk=encuesta_id)
            foto = Fotografia.objects.create(
                encuesta=encuesta,
                imagen=imagen,
                subido_por=request.user
            )
            return JsonResponse({
                'success': True,
                'foto': {
                    'id': foto.id,
                    'imagen_url': foto.imagen.url,
                    'fecha_subida': foto.fecha_subida.strftime('%d %b %Y %H:%M') if hasattr(foto, 'fecha_subida') and foto.fecha_subida else '',
                    'tipo': 'encuesta',
                    'encuesta': {
                        'titulo': encuesta.titulo,
                        'descripcion': encuesta.descripcion,
                        'fecha_creacion': encuesta.fecha_creacion.strftime('%d %b %Y %H:%M') if encuesta.fecha_creacion else 'Sin fecha',
                        'fecha_finalizacion': encuesta.fecha_finalizacion.strftime('%d %b %Y') if encuesta.fecha_finalizacion else 'Sin fecha'
                    }
                }
            })
        else:
            return JsonResponse({'success': False, 'error': 'Tipo de elemento no válido.'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Vistas para Bitácora del Sistema
@login_required
def bitacora_sistema(request):
    """
    Vista para mostrar la bitácora del sistema (solo superusuarios)
    """
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('inicio')
    
    # Obtener parámetros de filtrado
    accion_filter = request.GET.get('accion', '')
    tipo_objeto_filter = request.GET.get('tipo_objeto', '')
    usuario_filter = request.GET.get('usuario', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Obtener registros de bitácora ordenados por fecha y hora descendente
    registros = Bitacora.objects.all().order_by('-fecha_hora')
    
    # Aplicar filtros
    if accion_filter:
        registros = registros.filter(accion=accion_filter)
    
    if tipo_objeto_filter:
        registros = registros.filter(tipo_objeto=tipo_objeto_filter)
    
    if usuario_filter:
        registros = registros.filter(usuario__username__icontains=usuario_filter)
    
    # Aplicar filtros de fecha usando SQL directo si es necesario
    if fecha_desde or fecha_hasta:
        from django.db import connection
        
        # Construir la consulta SQL base
        sql_base = "SELECT * FROM encuesta_bitacora WHERE 1=1"
        params = []
        
        if fecha_desde:
            sql_base += " AND DATE(fecha_hora) >= %s"
            params.append(fecha_desde)
        
        if fecha_hasta:
            sql_base += " AND DATE(fecha_hora) <= %s"
            params.append(fecha_hasta)
        
        sql_base += " ORDER BY fecha_hora DESC"
        
        # Ejecutar consulta SQL directa
        with connection.cursor() as cursor:
            cursor.execute(sql_base, params)
            results = cursor.fetchall()
            
            # Obtener los IDs de los registros filtrados
            registro_ids = [row[0] for row in results]  # ID está en la primera columna
            
            # Filtrar el queryset original usando los IDs
            if registro_ids:
                registros = registros.filter(id__in=registro_ids)
            else:
                registros = registros.none()
    
    # Re-aplicar ordenamiento después de todos los filtros
    registros = registros.order_by('-fecha_hora')
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(registros, 50)  # 50 registros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas para el dashboard
    total_registros = Bitacora.objects.count()
    registros_hoy = Bitacora.objects.filter(fecha_hora__date=timezone.localdate()).count()
    acciones_mas_frecuentes = Bitacora.objects.values('accion').annotate(
        count=Count('accion')
    ).order_by('-count')[:5]
    
    usuarios_activos = Bitacora.objects.values('usuario__username').annotate(
        count=Count('usuario')
    ).order_by('-count')[:5]
    
    context = {
        'page_obj': page_obj,
        'total_registros': total_registros,
        'registros_hoy': registros_hoy,
        'acciones_mas_frecuentes': acciones_mas_frecuentes,
        'usuarios_activos': usuarios_activos,
        'accion_choices': Bitacora.ACCION_CHOICES,
        'tipo_objeto_choices': Bitacora.TIPO_OBJETO_CHOICES,
        'filtros': {
            'accion': accion_filter,
            'tipo_objeto': tipo_objeto_filter,
            'usuario': usuario_filter,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        }
    }
    
    return render(request, 'bitacora/listar.html', context)

@login_required
def restaurar_todo_papelera(request):
    if request.method == 'POST':
        try:
            # Restaurar todas las encuestas
            encuestas_restauradas = Encuesta.objects.filter(papelera=True)
            for encuesta in encuestas_restauradas:
                encuesta.papelera = False
                encuesta.save()
                registrar_bitacora(
                    accion='restaurar',
                    tipo_objeto='encuesta',
                    descripcion=f'Se restauró la encuesta "{encuesta.titulo}" desde la papelera (acción masiva)',
                    objeto_id=encuesta.id,
                    objeto_nombre=encuesta.titulo,
                    request=request
                )
            
            # Restaurar todos los encuestados
            encuestados_restaurados = Encuestado.objects.filter(papelera=True)
            for encuestado in encuestados_restaurados:
                encuestado.papelera = False
                encuestado.save()
                registrar_bitacora(
                    accion='restaurar',
                    tipo_objeto='encuestado',
                    descripcion=f'Se restauró el encuestado "{encuestado.nombre} {encuestado.apellido}" desde la papelera (acción masiva)',
                    objeto_id=encuestado.id,
                    objeto_nombre=f'{encuestado.nombre} {encuestado.apellido}',
                    request=request
                )
            
            total_restaurados = encuestas_restauradas.count() + encuestados_restaurados.count()
            
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': f'Se restauraron {total_restaurados} elementos correctamente.',
                    'total_restaurados': total_restaurados
                })
            else:
                messages.success(request, f'Se restauraron {total_restaurados} elementos correctamente.')
                return redirect('papelera')
                
        except Exception as e:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': f'Error al restaurar elementos: {str(e)}'
                })
            else:
                messages.error(request, f'Error al restaurar elementos: {str(e)}')
                return redirect('papelera')
    
    return redirect('papelera')

@login_required
def limpiar_todo_papelera(request):
    if request.method == 'POST':
        try:
            # Verificar contraseña del super usuario si se proporciona
            password = request.POST.get('password')
            # Validar contra el super usuario real
            superuser = User.objects.filter(is_superuser=True).first()
            if not password or not superuser or not superuser.check_password(password):
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({
                        'success': False,
                        'message': 'Contraseña de super usuario incorrecta'
                    })
                else:
                    messages.error(request, 'Contraseña de super usuario incorrecta')
                    return redirect('papelera')
            
            # Eliminar permanentemente todas las encuestas
            encuestas_eliminadas = Encuesta.objects.filter(papelera=True)
            for encuesta in encuestas_eliminadas:
                titulo = encuesta.titulo
                encuesta.delete()
                registrar_bitacora(
                    accion='eliminar',
                    tipo_objeto='encuesta',
                    descripcion=f'Se eliminó permanentemente la encuesta "{titulo}" (acción masiva)',
                    objeto_id=None,
                    objeto_nombre=titulo,
                    request=request
                )
            
            # Eliminar permanentemente todos los encuestados
            encuestados_eliminados = Encuestado.objects.filter(papelera=True)
            for encuestado in encuestados_eliminados:
                nombre_completo = f'{encuestado.nombre} {encuestado.apellido}'
                encuestado.delete()
                registrar_bitacora(
                    accion='eliminar',
                    tipo_objeto='encuestado',
                    descripcion=f'Se eliminó permanentemente el encuestado "{nombre_completo}" (acción masiva)',
                    objeto_id=None,
                    objeto_nombre=nombre_completo,
                    request=request
                )
            
            total_eliminados = encuestas_eliminadas.count() + encuestados_eliminados.count()
            
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': f'Se eliminaron permanentemente {total_eliminados} elementos.',
                    'total_eliminados': total_eliminados
                })
            else:
                messages.success(request, f'Se eliminaron permanentemente {total_eliminados} elementos.')
                return redirect('papelera')
                
        except Exception as e:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': f'Error al eliminar elementos: {str(e)}'
                })
            else:
                messages.error(request, f'Error al eliminar elementos: {str(e)}')
                return redirect('papelera')
    
    return redirect('papelera')