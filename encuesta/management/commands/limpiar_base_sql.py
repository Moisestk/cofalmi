from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Limpiar la base de datos usando SQL directo para evitar problemas de integridad'

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
                    'ADVERTENCIA: Este comando eliminará TODOS los datos de la base de datos.\n'
                    'Para confirmar, ejecuta: python manage.py limpiar_base_sql --confirmar'
                )
            )
            return

        self.stdout.write('Iniciando limpieza de la base de datos con SQL directo...')
        
        try:
            with connection.cursor() as cursor:
                # Desactivar temporalmente las verificaciones de claves foráneas
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                
                # Lista de tablas a limpiar (en orden inverso de dependencias)
                tables_to_clear = [
                    'encuesta_itemrespuesta',
                    'encuesta_respuesta',
                    'encuesta_opcionpregunta',
                    'encuesta_itemencuesta',
                    'encuesta_fotografia',
                    'encuesta_encuestado',
                    'encuesta_encuesta',
                ]
                
                for table in tables_to_clear:
                    try:
                        cursor.execute(f"TRUNCATE TABLE {table};")
                        self.stdout.write(f'Tabla {table} limpiada')
                    except Exception as e:
                        self.stdout.write(f'Error limpiando {table}: {str(e)}')
                        # Intentar DELETE en lugar de TRUNCATE si TRUNCATE falla
                        try:
                            cursor.execute(f"DELETE FROM {table};")
                            self.stdout.write(f'Tabla {table} limpiada con DELETE')
                        except Exception as e2:
                            self.stdout.write(f'Error con DELETE en {table}: {str(e2)}')
                
                # Reactivar las verificaciones de claves foráneas
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                
                self.stdout.write(
                    self.style.SUCCESS(
                        'Base de datos limpiada exitosamente!\n'
                        'Todos los datos han sido eliminados.'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error durante la limpieza: {str(e)}'
                )
            )
            raise
