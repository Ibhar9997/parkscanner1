# Deployment en Render

## Pasos para desplegar en Render

### 1. Preparar el repositorio
- Asegúrate de tener estos archivos en la raíz del proyecto:
  - `requirements.txt` ✓
  - `render.yaml` ✓
  - `.env.example` ✓
  - `manage.py` ✓

### 2. Crear cuenta en Render
- Ve a https://render.com
- Regístrate o inicia sesión

### 3. Conectar repositorio
- Ve a Dashboard → New + → Web Service
- Conecta tu repositorio de GitHub
- Selecciona este proyecto

### 4. Configurar el servicio
- **Name**: parkscanner (o el que prefieras)
- **Environment**: Python
- **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- **Start Command**: `gunicorn parkscanner.wsgi:application`
- **Plan**: Free (o el que prefieras)

### 5. Agregar variables de entorno
En Render Dashboard, ve a **Environment** y agrega:

```
DEBUG=False
SECRET_KEY=change-me-to-a-random-key
ALLOWED_HOSTS=parkscanner.onrender.com
```

### 6. Deploy
- Click en "Create Web Service"
- Espera a que Render construya e inicie la aplicación

## Comando de inicio

```bash
gunicorn parkscanner.wsgi:application
```

Este comando:
- Inicia el servidor web WSGI
- Ejecuta en el puerto que Render asigna (automático)
- Maneja solicitudes HTTP concurrentes

## Archivos de configuración creados

- **render.yaml**: Configuración de Render para build y start
- **requirements.txt**: Dependencias actualizadas con gunicorn y whitenoise
- **.env.example**: Variables de entorno necesarias
- **settings.py**: Actualizado para producción
  - Lee variables de entorno con `os.getenv()`
  - DEBUG en False por defecto
  - ALLOWED_HOSTS configurable
  - WhiteNoise habilitado para archivos estáticos

## Notas importantes

⚠️ **Cambiar SECRET_KEY en producción**
- Genera una nueva con: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- No uses la clave por defecto

⚠️ **Base de datos**
- Por defecto usa SQLite (db.sqlite3)
- Render reinicia la aplicación cada cierto tiempo, lo que puede borrar datos en SQLite
- Para producción, considera usar PostgreSQL en Render

⚠️ **Archivos estáticos**
- WhiteNoise maneja automáticamente CSS, JS, imágenes
- La carpeta `staticfiles/` se genera durante el deploy

