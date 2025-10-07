from django.contrib import admin
from .models import (
   
    Encuestado, Encuesta, ItemEncuesta, ItemRespuesta, Fotografia, Respuesta, OpcionPregunta
)

# Registro de modelos de encuestas}

admin.site.register(Encuestado)
admin.site.register(Encuesta)
admin.site.register(ItemEncuesta)
admin.site.register(ItemRespuesta)
admin.site.register(Fotografia)
admin.site.register(Respuesta)
admin.site.register(OpcionPregunta)


# Register your models here.
