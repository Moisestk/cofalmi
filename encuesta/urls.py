from django.urls import path, include
from . import views
from .views import CustomPasswordResetConfirmView
from django.conf import settings
from django.conf.urls.static import static
from .views import logout_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.login_view, name='login_view'),
    path('inicio', views.inicio, name='inicio'),
    path('perfil1', views.perfil1, name='perfil1'),
    path('logout', logout_view, name='logout_view'),
    path('login', views.login, name='login1'),
    path('captcha/', include('captcha.urls')),

    # Recuperación de contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_1.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done1.html'), name="password_reset_done"),
    path('password_reset_confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete1.html'), name='password_reset_complete'),

    path('usuarios', views.usuarios, name="usuarios"),
    path('usuarios/nuevo', views.nuevoUsuario, name="nuevo_usuario"),
    path('usuarios/editar/<int:id>', views.editarUsuario, name="editar_usuario"),
    path('usuarios/borrar/<int:usuario_id>/', views.borrar_usuario, name='borrar_usuario'),
    path('cambiar_password/<int:id>', views.cambiarPassword, name="cambiar_password"),
    path('editarUsuario/<int:id>', views.editarUsuario, name='editarUsuario'),
    path('usuarios/<str:accion>/<int:id>/', views.habilitarInhabilitarUsuario, name='habilitar_inhabilitar_usuario'),

    # ENCUESTADOS
    path('encuestados/', views.listar_encuestados, name='listar_encuestados'),
    path('encuestados/crear/', views.crear_encuestado, name='crear_encuestado'),
    path('encuestados/editar/<int:pk>/', views.editar_encuestado, name='editar_encuestado'),
    path('verificar-cedula/', views.verificar_cedula, name='verificar_cedula'),
    
    # ENCUESTAS
    path('encuestas/', views.listar_encuestas, name='listar_encuestas'),
    path('encuestas/crear/', views.crear_encuesta, name='crear_encuesta'),
    path('encuestas/desactivar/<int:encuesta_id>/', views.desactivar_encuesta, name='desactivar_encuesta'),
    path('encuestas/<int:encuesta_id>/editar/', views.editar_encuesta, name='editar_encuesta'),
    path('encuestas/<int:encuesta_id>/papelera/', views.enviar_a_papelera_encuesta, name='enviar_a_papelera_encuesta'),
    path('encuestas/generar-pdf/', views.generar_pdf_encuestas, name='generar_pdf_encuestas'),
    path('encuestas/<int:encuesta_id>/reabrir/', views.reabrir_encuesta, name='reabrir_encuesta'),
    path('encuestas/<int:encuesta_id>/', views.detalle_encuesta, name='detalle_encuesta'),  # Esta AL FINAL
    

    # PREGUNTAS
    path('pregunta/obtener/', views.obtener_pregunta, name='obtener_pregunta'),
    path('pregunta/editar/', views.editar_pregunta_ajax, name='editar_pregunta_ajax'),
    path('pregunta/eliminar/', views.eliminar_pregunta, name='eliminar_pregunta'),
    path('pregunta/detalles/', views.detalles_pregunta, name='detalles_pregunta'),
    path('encuestas/<int:encuesta_id>/agregar-pregunta/', views.agregar_pregunta, name='agregar_pregunta'),
    
    # RESPUESTAS
    path('preguntas/<int:item_encuesta_id>/agregar-respuesta/', views.agregar_respuesta, name='agregar_respuesta'),
   
    # RESPONDER ENCUESTA
    path('encuestas/<int:encuesta_id>/responder/', views.responder_encuesta, name='responder_encuesta'),
    
    # SELECCIONAR ENCUESTA Y ENCUESTADO
    path('aplicar/', views.seleccionar_encuesta_encuestado, name='seleccionar_encuesta_encuestado'),
    path('aplicar/<int:encuesta_id>/<int:encuestado_id>/', views.realizar_encuesta, name='realizar_encuesta'),
    path('reportes/', views.listar_reportes, name='listar_reportes'),
    path('reportes/<int:encuesta_id>/respondientes/', views.reportes_respondientes, name='reportes_respondientes'),
    path('reportes/<int:encuesta_id>/respondientes/', views.reportes_respondientes, name='reportes_respondientes'),
    path('respuesta/<int:respuesta_id>/', views.detalle_respuesta, name='detalle_respuesta'),
    
    # PAPELERA
    path('papelera/', views.papelera, name='papelera'),
    path('papelera/', views.papelera, name='listar_papelera'),
    path('papelera/eliminar/<int:respuesta_id>/', views.eliminar_respuesta, name='eliminar_respuesta'),
    path('papelera/enviar/<int:respuesta_id>/', views.enviar_a_papelera, name='enviar_a_papelera'),
    path('papelera/eliminar_encuesta/<int:encuesta_id>/', views.eliminar_encuesta, name='eliminar_encuesta'),
    path('papelera/restaurar_encuesta/<int:encuesta_id>/', views.restaurar_encuesta, name='restaurar_encuesta'),
    path('encuestados/papelera/<int:encuestado_id>/', views.enviar_a_papelera_encuestado, name='enviar_a_papelera_encuestado'),
    path('encuestados/restaurar/<int:encuestado_id>/', views.restaurar_encuestado, name='restaurar_encuestado'),
    path('encuestados/eliminar/<int:encuestado_id>/', views.eliminar_encuestado, name='eliminar_encuestado'),
    
    # ACCIONES MASIVAS PAPELERA
    path('papelera/restaurar-todo/', views.restaurar_todo_papelera, name='restaurar_todo_papelera'),
    path('papelera/limpiar-todo/', views.limpiar_todo_papelera, name='limpiar_todo_papelera'),

    # FOTOGRAFÍAS
    path('fotografias/', views.listar_fotografias, name='listar_fotografias'),
    path('fotografias/<int:foto_id>/', views.ver_fotografia, name='ver_fotografia'),
    path('fotografias/<int:foto_id>/editar/', views.editar_fotografia, name='editar_fotografia'),
    path('encuesta/<int:encuesta_id>/agregar-foto/', views.agregar_foto_encuesta, name='agregar_foto_encuesta'),
    path('fotografias/agregar/', views.agregar_fotografia_ajax, name='agregar_fotografia'),
    path('fotografias/<int:foto_id>/borrar/', views.borrar_fotografia, name='borrar_fotografia'),
    
    # Bitácora del Sistema
    path('bitacora/', views.bitacora_sistema, name='bitacora_sistema'),
    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)