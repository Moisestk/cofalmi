from django.core.management.base import BaseCommand
from django.db import transaction
from encuesta.models import (
    Encuesta, Encuestado, Fotografia, ItemEncuesta, 
    OpcionPregunta, ItemRespuesta, Respuesta
)

class Command(BaseCommand):
    help = 'Limpiar solo los datos de encuestas y encuestados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirmar la eliminación (requerido para ejecutar)'
        )

    def handle(self, *args, **options):
        if not options['confirmar']:
            self.stdout.write(
                self.style.ERROR(
                    'ADVERTENCIA: Este comando eliminará TODOS los datos de encuestas y encuestados.\n'
                    'Para confirmar, ejecuta: python manage.py limpiar_encuestas --confirmar'
                )
            )
            return

        self.stdout.write('Iniciando limpieza de datos de encuestas...')
        
        try:
            with transaction.atomic():
                # Eliminar en orden inverso de dependencias
                
                # 1. Eliminar respuestas
                self.stdout.write('Eliminando respuestas...')
                Respuesta.objects.all().delete()
                
                # 2. Eliminar items de respuestas
                self.stdout.write('Eliminando items de respuestas...')
                ItemRespuesta.objects.all().delete()
                
                # 3. Eliminar opciones de preguntas
                self.stdout.write('Eliminando opciones de preguntas...')
                OpcionPregunta.objects.all().delete()
                
                # 4. Eliminar items de encuestas
                self.stdout.write('Eliminando items de encuestas...')
                ItemEncuesta.objects.all().delete()
                
                # 5. Eliminar fotografías
                self.stdout.write('Eliminando fotografías...')
                Fotografia.objects.all().delete()
                
                # 6. Eliminar encuestados
                self.stdout.write('Eliminando encuestados...')
                Encuestado.objects.all().delete()
                
                # 7. Eliminar encuestas
                self.stdout.write('Eliminando encuestas...')
                Encuesta.objects.all().delete()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        'Datos de encuestas limpiados exitosamente!\n'
                        'Los usuarios del sistema se mantienen intactos.'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error durante la limpieza: {str(e)}'
                )
            )
            raise
