# 📊 Documentación del Dashboard Mejorado

## Archivos Creados y Modificados

### ✅ Archivos CSS
**Ubicación:** `encuesta/static/css/inicio.css`

**Contenido:**
- Estilos para el header del dashboard con gradiente
- Tarjetas de estadísticas con efectos hover
- Animaciones pulse para los iconos
- Estilos para las gráficas
- Diseño responsive

**Características:**
- Variables CSS para colores personalizados por categoría
- Transiciones suaves
- Sombras y efectos visuales modernos

---

### ✅ Archivos JavaScript
**Ubicación:** `encuesta/static/js/inicio/dashboard.js`

**Contenido:**
- Inicialización de 5 gráficas interactivas con Chart.js
- Manejo de datos del backend
- Configuración de colores y estilos
- Tooltips personalizados
- Fecha actual en el header

**Gráficas Implementadas:**
1. **Gráfica de Tendencia (Líneas)** - Muestra los últimos 30 días
2. **Gráfica de Distribución (Dona)** - Porcentajes totales
3. **Gráfica de Barras** - Encuestas de la última semana
4. **Gráfica de Área** - Encuestados de la última semana
5. **Gráfica Polar** - Comunidades de la última semana

---

### ✅ Archivo HTML
**Ubicación:** `encuesta/templates/inicio.html`

**Estructura:**
```django
{% extends "base.html" %}
{% load static %}

{% block css %}
<link href="{% static 'css/inicio.css' %}" rel="stylesheet">
{% endblock %}

{% block contenido %}
<!-- Contenido del dashboard -->
{% endblock %}

{% block scripts %}
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
    // Variables globales con datos del backend
    const labels = {{ labels_grafico|safe }};
    const dataEncuestas = {{ data_encuestas|safe }};
    const dataEncuestados = {{ data_encuestados|safe }};
    const dataComunidades = {{ data_comunidades|safe }};
    const totalEncuestas = {{ total_encuestas }};
    const totalEncuestados = {{ total_encuestados }};
    const totalComunidades = {{ total_comunidades }};
</script>
<script src="{% static 'js/inicio/dashboard.js' %}"></script>
{% endblock %}
```

---

## 🎨 Características del Diseño

### Header del Dashboard
- **Gradiente:** Morado a azul (#667eea → #764ba2)
- **Información:** Título, descripción y fecha actual
- **Responsive:** Se adapta a móviles

### Tarjetas de Estadísticas
Cada tarjeta tiene:
- **Borde superior** con gradiente único
- **Icono animado** con efecto pulse
- **Número grande** con gradiente en el texto
- **Indicador de tendencia** con badge verde
- **Efecto hover** que eleva la tarjeta

**Colores por categoría:**
- **Encuestas:** #667eea → #764ba2 (Morado)
- **Encuestados:** #f093fb → #f5576c (Rosa)
- **Comunidades:** #4facfe → #00f2fe (Azul)

### Gráficas Interactivas
- **Responsive:** Se adaptan al tamaño de pantalla
- **Tooltips:** Información detallada al pasar el mouse
- **Animaciones:** Suaves y profesionales
- **Colores consistentes:** Coinciden con las tarjetas

---

## 📁 Estructura de Archivos

```
encuesta/
├── static/
│   ├── css/
│   │   └── inicio.css          ✅ NUEVO
│   └── js/
│       └── inicio/
│           ├── dashboard.js    ✅ NUEVO
│           └── inicio.js       (archivo original, ahora no se usa)
└── templates/
    ├── inicio.html             ✅ ACTUALIZADO (versión limpia)
    ├── inicio_con_estilos_inline.html  (backup con estilos inline)
    └── inicio_old.html         (backup del diseño original)
```

---

## 🔧 Datos Requeridos del Backend

El archivo `views.py` debe pasar estos datos al template:

```python
{
    'total_encuestas': int,           # Total de encuestas
    'total_encuestados': int,         # Total de encuestados
    'total_comunidades': int,         # Total de comunidades
    'labels_grafico': JSON,           # Array de fechas (últimos 30 días)
    'data_encuestas': JSON,           # Array de conteos por día
    'data_encuestados': JSON,         # Array de conteos por día
    'data_comunidades': JSON,         # Array de conteos por día
}
```

**Ejemplo:**
```python
return render(request, 'inicio.html', {
    'total_encuestas': 45,
    'total_encuestados': 120,
    'total_comunidades': 8,
    'labels_grafico': json.dumps(['2025-01-01', '2025-01-02', ...]),
    'data_encuestas': json.dumps([2, 5, 3, ...]),
    'data_encuestados': json.dumps([10, 15, 8, ...]),
    'data_comunidades': json.dumps([1, 0, 2, ...]),
})
```

---

## 🚀 Cómo Usar

1. **Asegúrate de que Chart.js esté cargado:**
   - Ya está incluido en el template: `<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`

2. **Los archivos CSS y JS se cargan automáticamente:**
   - CSS: `{% static 'css/inicio.css' %}`
   - JS: `{% static 'js/inicio/dashboard.js' %}`

3. **Recarga el navegador:**
   - Ve a `http://127.0.0.1:8000/`
   - Verás el nuevo dashboard con todas las gráficas

---

## 🎯 Ventajas de Esta Estructura

### ✅ Separación de Responsabilidades
- **HTML:** Solo estructura
- **CSS:** Solo estilos
- **JS:** Solo lógica

### ✅ Mantenibilidad
- Fácil de modificar colores en `inicio.css`
- Fácil de agregar nuevas gráficas en `dashboard.js`
- HTML limpio y legible

### ✅ Reutilización
- Los estilos pueden usarse en otras páginas
- Las funciones JS son modulares

### ✅ Performance
- Los archivos CSS y JS se cachean en el navegador
- Carga más rápida en visitas posteriores

---

## 🔄 Archivos de Backup

Por seguridad, se guardaron copias:

1. **inicio_old.html** - Diseño original simple
2. **inicio_con_estilos_inline.html** - Versión con estilos inline (la que creamos primero)
3. **inicio.html** - Versión actual limpia (la que está activa)

Para volver a una versión anterior, simplemente renombra el archivo deseado a `inicio.html`.

---

## 📱 Responsive Design

El dashboard se adapta automáticamente a:
- **Desktop:** 3 columnas para las tarjetas
- **Tablet:** 2 columnas
- **Móvil:** 1 columna

Las gráficas también se ajustan al tamaño de pantalla.

---

## 🎨 Personalización

### Cambiar Colores
Edita `encuesta/static/css/inicio.css`:

```css
.stat-card.encuestas {
    --card-color-1: #TU_COLOR_1;
    --card-color-2: #TU_COLOR_2;
}
```

### Agregar Nueva Gráfica
1. Agrega el canvas en `inicio.html`:
```html
<canvas id="miNuevaGrafica"></canvas>
```

2. Agrega el código en `dashboard.js`:
```javascript
const miGraficaCtx = document.getElementById('miNuevaGrafica');
if (miGraficaCtx) {
    new Chart(miGraficaCtx.getContext('2d'), {
        // configuración
    });
}
```

---

## ✅ Checklist de Verificación

- [x] CSS creado en `static/css/inicio.css`
- [x] JS creado en `static/js/inicio/dashboard.js`
- [x] HTML actualizado con referencias externas
- [x] Backups creados
- [x] Datos del backend correctamente pasados
- [x] Chart.js cargado
- [x] Gráficas funcionando
- [x] Diseño responsive

---

**Fecha de creación:** 2025-10-01  
**Versión:** 1.0  
**Estado:** ✅ Completado y Funcional
