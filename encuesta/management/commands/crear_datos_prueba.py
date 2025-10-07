from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Crear exactamente 25 encuestas y 54 encuestados de prueba'

    def handle(self, *args, **options):
        self.stdout.write('Creando 25 encuestas y 54 encuestados de prueba...')
        
        try:
            with connection.cursor() as cursor:
                # Obtener o crear un usuario para las encuestas
                user, created = User.objects.get_or_create(
                    username='admin_prueba',
                    defaults={
                        'email': 'admin@prueba.com',
                        'first_name': 'Admin',
                        'last_name': 'Prueba',
                        'is_staff': True,
                        'is_superuser': True
                    }
                )
                
                # Crear exactamente 25 encuestas
                encuestas_creadas = 0
                for i in range(25):
                    fecha_creacion = timezone.now() - timedelta(days=random.randint(0, 29))
                    cursor.execute("""
                        INSERT INTO encuesta_encuesta 
                        (titulo, descripcion, fecha_creacion, usuario_id, activo, papelera) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, [
                        f'Encuesta de Prueba {i+1}',
                        f'Descripción detallada de la encuesta de prueba número {i+1} para evaluación del sistema.',
                        fecha_creacion,
                        user.id,
                        True,
                        False
                    ])
                    encuestas_creadas += 1
                
                # Crear exactamente 54 encuestados
                encuestados_creados = 0
                nombres = [
                    'Juan', 'María', 'Carlos', 'Ana', 'Luis', 'Carmen', 'Pedro', 'Laura', 
                    'Miguel', 'Sofia', 'Jorge', 'Elena', 'Roberto', 'Isabel', 'Fernando',
                    'Patricia', 'Diego', 'Monica', 'Andres', 'Gabriela', 'Ricardo', 'Valeria',
                    'Alejandro', 'Natalia', 'Sergio', 'Claudia', 'Rafael', 'Beatriz', 'Oscar',
                    'Martha', 'Daniel', 'Lorena', 'Antonio', 'Silvia', 'Francisco', 'Adriana',
                    'Manuel', 'Teresa', 'Javier', 'Rosa', 'Eduardo', 'Marta', 'Alberto',
                    'Cristina', 'Vicente', 'Pilar', 'Jose', 'Dolores', 'Angel', 'Rocio',
                    'Enrique', 'Concepcion', 'Pablo', 'Mercedes'
                ]
                apellidos = [
                    'García', 'Rodríguez', 'Martínez', 'Hernández', 'López', 'González', 
                    'Pérez', 'Sánchez', 'Ramírez', 'Cruz', 'Flores', 'Torres', 'Vargas',
                    'Jiménez', 'Ruiz', 'Díaz', 'Morales', 'Ramos', 'Ortega', 'Herrera',
                    'Mendoza', 'Castillo', 'Romero', 'Guerrero', 'Medina', 'Moreno', 'Silva',
                    'Vega', 'Rivera', 'Contreras', 'Espinoza', 'Aguilar', 'Rojas', 'Peña',
                    'Molina', 'Campos', 'Sandoval', 'Fuentes', 'Delgado', 'Vásquez'
                ]
                
                for i in range(54):
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
                        str(random.randint(10000000, 99999999)),
                        random.choice(['masculino', 'femenino']),
                        f"0{random.randint(400, 426)}{random.randint(1000000, 9999999)}",
                        fecha_registro,
                        False
                    ])
                    encuestados_creados += 1
                
                # Crear algunas fotografías (aproximadamente 1 por cada 2 encuestas)
                fotografias_creadas = 0
                cursor.execute("SELECT id FROM encuesta_encuesta")
                encuesta_ids = [row[0] for row in cursor.fetchall()]
                
                for i in range(12):  # 12 fotografías
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
                        f'Datos de prueba creados exitosamente:\n'
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
