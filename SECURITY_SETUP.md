# Configuración de Seguridad del Proyecto

## Variables de Entorno

Este proyecto ahora utiliza variables de entorno para proteger información sensible como claves secretas y credenciales de correo electrónico.

### Configuración Inicial

1. **Instalar la dependencia necesaria:**
   ```bash
   pip install python-decouple
   ```

2. **Configurar el archivo .env:**
   - Ya existe un archivo `.env` en la raíz del proyecto con tus credenciales actuales
   - Este archivo **NO debe ser compartido** ni subido a repositorios públicos
   - El archivo `.gitignore` ya está configurado para excluir `.env`

3. **Estructura del archivo .env:**
   ```
   SECRET_KEY=tu-clave-secreta-django
   DEBUG=True
   EMAIL_HOST_USER=tu-email@gmail.com
   EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicacion-gmail
   DEFAULT_FROM_EMAIL=tu-email@gmail.com
   ```

### Para Otros Desarrolladores

Si compartes este proyecto con otros desarrolladores:

1. Copia el archivo `.env.example` a `.env`
2. Completa las variables con tus propias credenciales
3. Nunca compartas tu archivo `.env` real

### Generación de Nueva SECRET_KEY

Para generar una nueva SECRET_KEY de Django (recomendado para producción):

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Configuración de Gmail

Para usar Gmail con Django:

1. Activa la verificación en dos pasos en tu cuenta de Gmail
2. Genera una "Contraseña de aplicación" específica
3. Usa esa contraseña en `EMAIL_HOST_PASSWORD`

### Modo Producción

Antes de desplegar a producción:

1. Cambia `DEBUG=False` en el archivo `.env`
2. Genera una nueva `SECRET_KEY` única
3. Configura `ALLOWED_HOSTS` en `settings.py` con tu dominio
4. Usa variables de entorno del servidor de producción en lugar del archivo `.env`

## Archivos Importantes

- **`.env`**: Contiene las credenciales reales (NO compartir)
- **`.env.example`**: Plantilla para otros desarrolladores
- **`.gitignore`**: Excluye archivos sensibles del control de versiones
- **`settings.py`**: Ahora usa `config()` para leer variables de entorno

## Verificación

Para verificar que todo funciona correctamente:

```bash
python manage.py check
```

Si hay errores relacionados con variables de entorno, verifica que tu archivo `.env` existe y contiene todas las variables necesarias.
