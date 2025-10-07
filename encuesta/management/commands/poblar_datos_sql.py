from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Poblar el dashboard con datos usando SQL directo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=50,
            help='Cantidad de registros a crear (default: 50)'
        )

    def handle(self, *args, **options):
        cantidad = options['cantidad']
        
        self.stdout.write('Creando datos de ejemplo para el dashboard con SQL directo...')
        
        try:
            with connection.cursor() as cursor:
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
                
                # Crear encuestas con SQL directo
                encuestas_creadas = 0
                for i in range(cantidad):
                    fecha_creacion = timezone.now() - timedelta(days=random.randint(0, 29))
                    cursor.execute("""
                        INSERT INTO encuesta_encuesta 
                        (titulo, descripcion, fecha_creacion, usuario_id, activo, papelera) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, [
                        f'Encuesta de Ejemplo {i+1}',
                        f'Descripción de la encuesta de ejemplo número {i+1}',
                        fecha_creacion,
                        user.id,
                        True,
                        False
                    ])
                    encuestas_creadas += 1
                
                # Crear encuestados con SQL directo
                encuestados_creados = 0
                nombres = ['Juan', 'María', 'Carlos', 'Ana', 'Luis', 'Carmen', 'Pedro', 'Laura', 'Miguel', 'Sofia']
                apellidos = ['García', 'Rodríguez', 'Martínez', 'Hernández', 'López', 'González', 'Pérez', 'Sánchez', 'Ramírez', 'Cruz']
                
                for i in range(cantidad * 2):
                    fecha_registro = timezone.now() - timedelta(days=random.randint(0, 29))
                    nombre = random.choice(nombres)
                    apellido = random.choice(apellidos)
                    
                    cursor.execute("""
                        INSERT INTO encuesta_encuestado 
                        (nombre, apellido, tipo_cedula, cedula_numero, genero, telefono, fecha_registro, papelera) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        nombre,
                        apellido,
                        random.choice(['V', 'E']),
                        str(random.randint(1000000, 99999999)),
                        random.choice(['masculino', 'femenino']),
                        f"0{random.randint(400, 426)}{random.randint(1000000, 9999999)}",
                        fecha_registro,
                        False
                    ])
                    encuestados_creados += 1
                
                # Crear fotografías con SQL directo
                fotografias_creadas = 0
                cursor.execute("SELECT id FROM encuesta_encuesta")
                encuesta_ids = [row[0] for row in cursor.fetchall()]
                
                for i in range(cantidad // 2):
                    encuesta_id = random.choice(encuesta_ids)
                    
                    cursor.execute("""
                        INSERT INTO encuesta_fotografia 
                        (imagen, fecha_subida, subido_por_id, encuesta_id) 
                        VALUES (%s, %s, %s, %s)
                    """, [
                        'encuestas/fotos/placeholder.jpg',
                        timezone.now() - timedelta(days=random.randint(0, 29)),
                        user.id,
                        encuesta_id
                    ])
                    fotografias_creadas += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Datos creados exitosamente:\n'
                        f'- {encuestas_creadas} encuestas\n'
                        f'- {encuestados_creados} encuestados\n'
                        f'- {fotografias_creadas} fotografías'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error durante la creación: {str(e)}'
                )
            )
            raise
