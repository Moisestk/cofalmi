from django.core.management.base import BaseCommand
from encuesta.models import ServicioBasico

class Command(BaseCommand):
    help = 'Pobla la base de datos con servicios básicos'

    def handle(self, *args, **options):
        # Crear servicios básicos
        servicios_data = [
            {'nombre': 'Agua', 'descripcion': 'Servicio de suministro de agua potable'},
            {'nombre': 'Luz', 'descripcion': 'Servicio de energía eléctrica'},
            {'nombre': 'Limpieza', 'descripcion': 'Servicio de recolección de basura y limpieza'},
            {'nombre': 'Gas', 'descripcion': 'Servicio de gas doméstico'},
            {'nombre': 'Internet', 'descripcion': 'Servicio de conexión a internet'},
            {'nombre': 'Teléfono', 'descripcion': 'Servicio de telefonía fija'},
            {'nombre': 'Cable', 'descripcion': 'Servicio de televisión por cable'},
            {'nombre': 'Alcantarillado', 'descripcion': 'Servicio de alcantarillado y drenaje'},
            {'nombre': 'Seguridad', 'descripcion': 'Servicio de seguridad comunitaria'},
            {'nombre': 'Transporte', 'descripcion': 'Servicio de transporte público'},
        ]
        
        for servicio_data in servicios_data:
            servicio, created = ServicioBasico.objects.get_or_create(
                nombre=servicio_data['nombre'],
                defaults={'descripcion': servicio_data['descripcion']}
            )
            if created:
                self.stdout.write(f'Creado servicio: {servicio.nombre}')
            else:
                self.stdout.write(f'Servicio ya existe: {servicio.nombre}')
        
        self.stdout.write(
            self.style.SUCCESS('¡Servicios básicos creados exitosamente!')
        )
