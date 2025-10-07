from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from django.contrib.auth.models import User
from encuesta.models import Encuesta, Encuestado, Fotografia

class Command(BaseCommand):
    help = 'Poblar el dashboard con datos de ejemplo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=50,
            help='Cantidad de registros a crear (default: 50)'
        )

    def handle(self, *args, **options):
        cantidad = options['cantidad']
        
        self.stdout.write('Creando datos de ejemplo para el dashboard...')
        
        # Obtener o crear un usuario para las encuestas
        user, created = User.objects.get_or_create(
            username='admin_dashboard',
            defaults={
                'email': 'admin@dashboard.com',
                'first_name': 'Admin',
                'last_name': 'Dashboard',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        # Crear encuestas
        encuestas_creadas = 0
        for i in range(cantidad):
            # Crear fechas en los últimos 30 días
            fecha_creacion = timezone.now() - timedelta(days=random.randint(0, 29))
            encuesta = Encuesta.objects.create(
                titulo=f'Encuesta de Ejemplo {i+1}',
                descripcion=f'Descripción de la encuesta de ejemplo número {i+1}',
                usuario=user,
                papelera=False
            )
            # Usar update() para cambiar la fecha después de crear
            Encuesta.objects.filter(id=encuesta.id).update(fecha_creacion=fecha_creacion)
            encuestas_creadas += 1
        
        # Crear encuestados
        encuestados_creados = 0
        nombres = ['Juan', 'María', 'Carlos', 'Ana', 'Luis', 'Carmen', 'Pedro', 'Laura', 'Miguel', 'Sofia']
        apellidos = ['García', 'Rodríguez', 'Martínez', 'Hernández', 'López', 'González', 'Pérez', 'Sánchez', 'Ramírez', 'Cruz']
        
        for i in range(cantidad * 2):  # Más encuestados que encuestas
            # Crear fechas en los últimos 30 días
            fecha_registro = timezone.now() - timedelta(days=random.randint(0, 29))
            nombre = random.choice(nombres)
            apellido = random.choice(apellidos)
            
            encuestado = Encuestado.objects.create(
                nombre=nombre,
                apellido=apellido,
                tipo_cedula=random.choice(['V', 'E']),
                cedula_numero=str(random.randint(1000000, 99999999)),
                genero=random.choice(['masculino', 'femenino']),
                telefono=f"0{random.randint(400, 426)}{random.randint(1000000, 9999999)}",
                papelera=False
            )
            # Usar update() para cambiar la fecha después de crear
            Encuestado.objects.filter(id=encuestado.id).update(fecha_registro=fecha_registro)
            encuestados_creados += 1
        
        # Crear fotografías
        fotografias_creadas = 0
        encuestas_disponibles = list(Encuesta.objects.all())
        
        for i in range(cantidad // 2):  # Menos fotografías que encuestas
            encuesta = random.choice(encuestas_disponibles)
            
            fotografia = Fotografia.objects.create(
                imagen='encuestas/fotos/placeholder.jpg',  # Necesitarías tener una imagen placeholder
                encuesta=encuesta,
                subido_por=user
            )
            fotografias_creadas += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Datos creados exitosamente:\n'
                f'- {encuestas_creadas} encuestas\n'
                f'- {encuestados_creados} encuestados\n'
                f'- {fotografias_creadas} fotografías'
            )
        )
        
        self.stdout.write(
            self.style.WARNING(
                'Nota: Las fotografías usan una imagen placeholder. '
                'Para ver imágenes reales, sube fotografías manualmente.'
            )
        )
