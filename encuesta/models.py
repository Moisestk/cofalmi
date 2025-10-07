from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.db.models import Q 

# Create your models here.
    
class Configuracion(models.Model):
    logo = models.ImageField(upload_to='logo', null=True, blank=True)
    
    def __str__(self):
        return self.logo.name if self.logo else "Sin Logo" 
 
    
# En Perfil
class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    avatar = models.ImageField(
        upload_to="uploads/perfiles/", verbose_name="Avatar", blank=True, null=True)
    def __str__(self):
        return str(self.usuario)
    def delete(self, using=None, keep_parents=False):  # Corrige el typo aquí
        if self.avatar.name:
            self.avatar.storage.delete(self.avatar.name)
        super().delete(using=using, keep_parents=keep_parents)


def crear_perfil(sender, instance, created, **kwargs):
    if created:
        user_profile = Perfil(usuario=instance)
        user_profile.save()


post_save.connect(crear_perfil, sender=User)


class Encuestado(models.Model):
    GENERO_CHOICES = [
    ('masculino', 'Masculino'),
    ('femenino', 'Femenino'),
    ]
    TIPO_CEDULA_CHOICES = [
        ('V', 'Venezolano'),
        ('E', 'Extranjero'),
    ]
    GENERO_CHOICES = [('masculino', 'Masculino'), ('femenino', 'Femenino')]
    TIPO_CEDULA_CHOICES = [('V', 'Venezolano'), ('E', 'Extranjero')]
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    tipo_cedula = models.CharField(max_length=1, choices=TIPO_CEDULA_CHOICES, default='V')
    cedula_numero = models.CharField(max_length=9) 
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES)
    telefono = models.CharField(max_length=11, blank=True, null=True)
    direccion = models.TextField(max_length=255, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    papelera = models.BooleanField(default=False)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    ubicacion_administrativa = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - C.I: {self.tipo_cedula}{self.cedula_numero}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cedula_numero'], 
                condition=Q(papelera=False),
                name='unique_cedula_if_not_in_papelera'
            )
        ]

class Encuesta(models.Model):
    titulo = models.CharField(max_length=255, blank=False, null=False)
    descripcion = models.TextField(blank=True, null=True)
    fecha_finalizacion = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    papelera = models.BooleanField(default=False)
    def __str__(self):
        return self.titulo

class ItemEncuesta(models.Model):
    TIPO_PREGUNTA_CHOICES = [
    ('texto', 'Texto'),
    ('opcion_multiple', 'Opción Múltiple'),
    ('opcion_unica', 'Opción Única'),
    ('si_no', 'Sí/No'),
    ]
    TIPO_RESPUESTA_CHOICES = [
    ('texto', 'Texto'),
    ('opcion_multiple', 'Opción Múltiple'),
    ('opcion_unica', 'Opción Única'),
    ('si_no', 'Sí/No'),
    ]   
    texto_pregunta = models.CharField(max_length=255)
    tipo_pregunta = models.CharField(max_length=20, choices=TIPO_PREGUNTA_CHOICES)
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE, related_name='items')
    tipo_respuesta = models.CharField(max_length=20, choices=TIPO_RESPUESTA_CHOICES)
    orden = models.IntegerField(default=0)
    requerida = models.BooleanField(default=False)
    titulo_campo_texto = models.CharField( max_length=100, blank=True,null=True, help_text="Título del campo de texto adicional para respuesta 'Sí'.")
    def clean(self):
        # Si el tipo_respuesta es 'abierta', lo cambiamos a 'texto'
        if self.tipo_respuesta == 'abierta':
            self.tipo_respuesta = 'texto'

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.texto_pregunta
    

class OpcionPregunta(models.Model):
    item_encuesta = models.ForeignKey(ItemEncuesta, on_delete=models.CASCADE, related_name='opciones')
    texto_opcion = models.CharField(max_length=255)

    def __str__(self):
        return self.texto_opcion
    
class ItemRespuesta(models.Model):
    item_encuesta = models.ForeignKey(ItemEncuesta, on_delete=models.CASCADE, related_name='respuestas')
    encuestado = models.ForeignKey(Encuestado, on_delete=models.CASCADE, related_name='respuestas')
    respuesta = models.ForeignKey('Respuesta', on_delete=models.CASCADE, related_name='items_respuesta', null=True, blank=True)
    texto_respuesta = models.TextField(max_length=255, blank=True, null=True)
    valor_respuesta = models.TextField(max_length=255, blank=True, null=True)
    opcion = models.ForeignKey(OpcionPregunta, on_delete=models.SET_NULL, null=True, blank=True, related_name='respuestas_opcion')
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Respuesta {self.id} - {self.item_encuesta.texto_pregunta}"

class Fotografia(models.Model):
    imagen = models.ImageField(upload_to='encuestas/fotos/')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    encuesta = models.ForeignKey('Encuesta', on_delete=models.CASCADE, related_name='fotografias', null=True, blank=True)
    
    def __str__(self):
        if self.encuesta:
            return f"Foto de {self.encuesta.titulo}"
        return str(self.imagen)

# 
class Respuesta(models.Model):
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE)
    encuestado = models.ForeignKey(Encuestado, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ubicacion_geografica = models.CharField(max_length=255, blank=True, null=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    papelera = models.BooleanField(default=False)
    def __str__(self):
        return f"Respuesta {self.id} - Encuesta {self.encuesta.titulo}"
    
# Modelo para Bitácora del Sistema
class Bitacora(models.Model):
    ACCION_CHOICES = [
        ('crear', 'Crear'),
        ('editar', 'Editar'),
        ('eliminar', 'Eliminar'),
        ('activar', 'Activar'),
        ('desactivar', 'Desactivar'),
        ('finalizar', 'Finalizar'),
        ('reabrir', 'Reabrir'),
        ('enviar', 'Enviar'),
        ('subir', 'Subir'),
        ('descargar', 'Descargar'),
        ('acceder', 'Acceder'),
        ('iniciar_sesion', 'Iniciar Sesión'),
        ('cerrar_sesion', 'Cerrar Sesión'),
        ('limpiar', 'Limpiar'),
        ('restaurar', 'Restaurar'),
    ]
    
    TIPO_OBJETO_CHOICES = [
        ('encuesta', 'Encuesta'),
        ('encuestado', 'Encuestado'),
        ('pregunta', 'Pregunta'),
        ('respuesta', 'Respuesta'),
        ('fotografia', 'Fotografía'),
        ('usuario', 'Usuario'),
        ('sistema', 'Sistema'),
        ('base_datos', 'Base de Datos'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES, verbose_name="Acción")
    tipo_objeto = models.CharField(max_length=20, choices=TIPO_OBJETO_CHOICES, verbose_name="Tipo de Objeto")
    descripcion = models.TextField(verbose_name="Descripción")
    objeto_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID del Objeto")
    objeto_nombre = models.CharField(max_length=255, null=True, blank=True, verbose_name="Nombre del Objeto")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    user_agent = models.TextField(null=True, blank=True, verbose_name="User Agent")
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    
    class Meta:
        verbose_name = "Bitácora"
        verbose_name_plural = "Bitácoras"
        ordering = ['-fecha_hora']
        
    def __str__(self):
        return f"{self.usuario.username} - {self.get_accion_display()} {self.get_tipo_objeto_display()} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"

# Modelos para las encuestas externas
    