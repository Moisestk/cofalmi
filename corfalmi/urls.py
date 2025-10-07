from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('encuesta/', include("django.contrib.auth.urls")),  # Corregido el nombre del path
    path('', include("encuesta.urls")),  # Todas las rutas de tu app principal
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)