from django.core.management.base import BaseCommand
from encuesta.models import Patologia, Medicamento, InsumoMedico

class Command(BaseCommand):
    help = 'Pobla la base de datos con datos médicos de ejemplo'

    def handle(self, *args, **options):
        # Crear patologías
        patologias_data = [
            'Diabetes',
            'Hipertensión',
            'Asma',
            'Artritis',
            'Enfermedad cardíaca',
            'Depresión',
            'Ansiedad',
            'Migraña',
            'Epilepsia',
            'Enfermedad renal'
        ]
        
        for patologia_nombre in patologias_data:
            patologia, created = Patologia.objects.get_or_create(nombre=patologia_nombre)
            if created:
                self.stdout.write(f'Creada patología: {patologia_nombre}')
        
        # Crear medicamentos
        medicamentos_data = [
            'Metformina',
            'Losartán',
            'Salbutamol',
            'Ibuprofeno',
            'Paracetamol',
            'Omeprazol',
            'Atorvastatina',
            'Amlodipino',
            'Sertralina',
            'Lorazepam'
        ]
        
        for medicamento_nombre in medicamentos_data:
            medicamento, created = Medicamento.objects.get_or_create(nombre=medicamento_nombre)
            if created:
                self.stdout.write(f'Creado medicamento: {medicamento_nombre}')
        
        # Crear insumos médicos
        insumos_data = [
            'Jeringas',
            'Tiras reactivas',
            'Inhalador',
            'Tensiómetro',
            'Glucómetro',
            'Termómetro',
            'Vendas',
            'Gasas',
            'Alcohol',
            'Guantes quirúrgicos'
        ]
        
        for insumo_nombre in insumos_data:
            insumo, created = InsumoMedico.objects.get_or_create(nombre=insumo_nombre)
            if created:
                self.stdout.write(f'Creado insumo: {insumo_nombre}')
        
        self.stdout.write(
            self.style.SUCCESS('¡Datos médicos creados exitosamente!')
        )
