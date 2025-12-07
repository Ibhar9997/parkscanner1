# 📱 ARQUETURA VISUAL DE MUSEQR

## 🏗️ ESTRUCTURA DEL PROYECTO

```
parkscanner/
│
├── 📄 manage.py                          # Gestión de Django
├── 📄 db.sqlite3                         # Base de datos (generada)
├── 📄 requirements.txt                   # Dependencias
│
├── 📚 DOCUMENTACIÓN
│   ├── README_MUSEQR.md                  # Documentación completa
│   ├── INICIO_RAPIDO.md                  # Guía de inicio rápido
│   ├── GUIA_ROLES.md                     # Guía por rol de usuario
│   ├── IMPLEMENTACION.md                 # Este resumen
│   └── ARQUITECTURA.md                   # (Este archivo)
│
├── 🔧 SCRIPTS ÚTILES
│   ├── init_data.py                      # Inicializar con datos
│   └── crear_usuario_demo.py             # Crear usuario de demo
│
├── parkscanner/                          # Configuración principal
│   ├── settings.py                       # ⭐ Actualizado con qrmuseum
│   ├── urls.py                           # ⭐ Include de qrmuseum.urls
│   ├── asgi.py
│   ├── wsgi.py
│   └── __pycache__/
│
├── qrmuseum/                             # 🆕 APP PRINCIPAL
│   ├── models.py                         # ⭐ 6 modelos creados
│   │   ├── MuseoConfig
│   │   ├── QRCode
│   │   ├── ContenidoQR
│   │   ├── ProgresoUsuario
│   │   ├── Comentario
│   │   └── UsuarioMuseo
│   │
│   ├── views.py                          # ⭐ 25 vistas creadas
│   │   ├── Vistas públicas (4)
│   │   ├── Vistas de usuario (5)
│   │   └── Vistas de admin (11)
│   │
│   ├── forms.py                          # ⭐ 6 formularios
│   ├── urls.py                           # ⭐ 23 rutas
│   ├── admin.py                          # ⭐ Registros en admin
│   ├── apps.py
│   ├── tests.py
│   │
│   ├── migrations/                       # 🆕 Migraciones de BD
│   │   ├── 0001_initial.py               # Migración inicial
│   │   └── __init__.py
│   │
│   └── __pycache__/
│
├── templates/                            # 🆕 TEMPLATES HTML
│   ├── base.html                         # Template base
│   │
│   ├── 🟢 PÚBLICOS (3)
│   │   ├── inicio.html
│   │   ├── login.html
│   │   └── registro.html
│   │
│   ├── 👤 USUARIO (5)
│   │   ├── escanear_qr.html             # Con jsQR
│   │   ├── contenido_qr.html            # Multimedia
│   │   ├── mi_progreso.html
│   │   └── editar_perfil.html
│   │
│   └── 👨‍💼 ADMIN (9)
│       ├── admin/
│       │   ├── dashboard.html
│       │   ├── qrs_list.html
│       │   ├── qr_form.html
│       │   ├── contenido_form.html
│       │   ├── comentarios.html
│       │   ├── moderar_comentario.html
│       │   ├── config_form.html
│       │   ├── usuarios.html
│       │   ├── estadisticas.html
│       │   └── confirmar_eliminar.html
│
└── media/                                # 🆕 ARCHIVOS MULTIMEDIA
    ├── qrcodes/                          # Códigos QR generados
    ├── contenido/
    │   ├── imagenes/                     # Imágenes de QRs
    │   ├── videos/                       # Videos educativos
    │   ├── audios/                       # Archivos de audio
    │   └── archivos/                     # PDFs y documentos
    ├── avatares/                         # Avatares de usuarios
    └── logos/                            # Logos del museo
```

## 🔄 FLUJO DE DATOS

### Flujo 1: Registro y Login de Usuario

```
Usuario anónimo
    ↓
[/registro/] - Formulario de registro
    ↓
✅ Usuario creado en Django
✅ UsuarioMuseo creado automáticamente
    ↓
[/login/] - Login
    ↓
Sesión iniciada
    ↓
Panel de usuario desbloqueado
```

### Flujo 2: Escaneo de QR y Progreso

```
Usuario autenticado
    ↓
[/escanear/] - Cámara abierta (jsQR)
    ↓
Escanea QR
    ↓
jsQR detecta código
    ↓
URL: /qr/<uuid>/
    ↓
Vista procesar_qr()
    ↓
✅ ProgresoUsuario creado/actualizado
✅ Puntos agregados (+10)
✅ UsuarioMuseo.total_qrs_escaneados incrementado
    ↓
[/contenido_qr.html] - Contenido multimedia mostrado
    ↓
Usuario puede dejar comentario
    ↓
Comentario creado (moderado=False)
    ↓
Aparece en [/admin/comentarios/]
```

### Flujo 3: Administración de QR

```
Admin en [/admin/dashboard/]
    ↓
→ [/admin/qrs/] - Ver lista de QRs
    ↓
→ [/admin/qr/crear/] - Crear nuevo
    ↓
QRCodeForm validado
    ↓
✅ QRCode creado
✅ Código QR generado automáticamente
✅ Imagen QR guardada en /media/qrcodes/
    ↓
Opción: Agregar contenido
    ↓
→ [/admin/qr/<id>/contenido/]
    ↓
ContenidoQRForm validado
    ↓
✅ ContenidoQR creado
✅ Archivos multimedia guardados
✅ Información educativa guardada
    ↓
QR listo para usuarios
```

## 📊 MODELO DE DATOS (Relaciones)

```
User (Django)
  ↓
  ├─→ OneToOne UsuarioMuseo
  │            ├─ Apodo
  │            ├─ Avatar
  │            ├─ Puntos
  │            └─ Nivel
  │
  ├─→ ForeignKey ProgresoUsuario
  │            ├─ qr_visitado (→ QRCode)
  │            ├─ fecha_visita
  │            └─ tiempo_permanencia
  │
  └─→ ForeignKey Comentario
               ├─ contenido_qr (→ ContenidoQR)
               ├─ calificacion
               └─ texto

QRCode
  ├─ id_unico (UUID)
  ├─ titulo
  ├─ numero_secuencial
  ├─ qr_code_image
  │
  └─→ OneToOne ContenidoQR
               ├─ tipo_contenido
               ├─ imagen
               ├─ video
               ├─ audio
               ├─ datos_historicos
               ├─ datos_cientificos
               └─ curiosidades
                    ↓
                    ├─→ ForeignKey Comentario[]
                              ├─ usuario
                              ├─ calificacion
                              └─ moderado

MuseoConfig
  ├─ nombre
  ├─ descripcion
  ├─ ubicacion
  └─ imagen_logo
```

## 🎨 INTERFAZ DE USUARIO

### Páginas Públicas

```
┌─────────────────────────────────┐
│         NAVBAR                  │
│  MuseoQR  │ Login │ Registrarse │
└─────────────────────────────────┘
        │
        ├─→ [INICIO]
        │   ├─ Nombre del museo
        │   ├─ Descripción
        │   └─ [Botón] Probar Ahora
        │          ↓
        │   └─→ [LOGIN REQUIRED]
        │
        ├─→ [LOGIN]
        │   ├─ Username
        │   ├─ Password
        │   └─ [Enviar]
        │
        └─→ [REGISTRO]
            ├─ Username
            ├─ Nombre completo
            ├─ Email
            ├─ Contraseña
            └─ [Crear Cuenta]
```

### Páginas de Usuario

```
┌─────────────────────────────────────────────────────┐
│  MuseoQR │ Escanear | Mi Progreso | Perfil | Logout │
└─────────────────────────────────────────────────────┘
        │
        ├─→ [INICIO - Autenticado]
        │   ├─ [Avatar]
        │   ├─ Nivel: 5
        │   ├─ Puntos: 150 🏆
        │   ├─ QRs: 15/30 (50%)
        │   ├─ [Escanear QR]
        │   └─ [Ver Progreso]
        │
        ├─→ [ESCANEAR QR]
        │   ├─ [Cámara]
        │   └─ [O entrada manual UUID]
        │
        ├─→ [CONTENIDO QR]
        │   ├─ Imagen
        │   ├─ Video
        │   ├─ Texto
        │   ├─ [Dejar Comentario]
        │   └─ [Comentarios previos]
        │
        ├─→ [MI PROGRESO]
        │   ├─ Avatar
        │   ├─ Nivel y Puntos
        │   ├─ Barra de Progreso
        │   ├─ QRs Escaneados
        │   └─ Mis Comentarios
        │
        └─→ [EDITAR PERFIL]
            ├─ Apodo del juego
            └─ Avatar
```

### Páginas de Administrador

```
┌────────────────────────────────────────────────────────┐
│  MuseoQR │ Admin Dashboard | Usuarios | Logout │ Super │
└────────────────────────────────────────────────────────┘
        │
        ├─→ [DASHBOARD]
        │   ├─ Stats: 25 QRs, 150 usuarios
        │   ├─ Menú rápido a todas funciones
        │   └─ Indicadores de actividad
        │
        ├─→ [GESTIONAR QRs]
        │   ├─ [Crear QR]
        │   │   ├─ # Secuencial
        │   │   ├─ Título
        │   │   └─ [QR generado automáticamente]
        │   │
        │   ├─ [Editar QR]
        │   │   └─ [Agregar contenido multimedia]
        │   │       ├─ Imagen
        │   │       ├─ Video
        │   │       ├─ Audio
        │   │       ├─ Info histórica
        │   │       ├─ Info científica
        │   │       └─ Curiosidades
        │   │
        │   └─ [Eliminar QR]
        │       └─ [Confirmación]
        │
        ├─→ [COMENTARIOS]
        │   ├─ Filtro: Todos/Pendientes/Aprobados
        │   ├─ [Moderar]
        │   │   ├─ [Aprobar]
        │   │   └─ [Rechazar]
        │   └─ Paginación (20 por página)
        │
        ├─→ [USUARIOS]
        │   ├─ Tabla de usuarios
        │   ├─ Nivel, Puntos, QRs escaneados
        │   └─ Paginación (20 por página)
        │
        ├─→ [ESTADÍSTICAS]
        │   ├─ Métricas: Usuarios, QRs, Escaneos
        │   ├─ Top 10 usuarios
        │   ├─ QRs más visitados
        │   └─ Gráficos de participación
        │
        └─→ [CONFIGURACIÓN]
            ├─ Nombre del museo
            ├─ Descripción
            ├─ Ubicación
            └─ Logo
```

## 🔐 AUTENTICACIÓN Y AUTORIZACIÓN

```
Solicitud HTTP
    ↓
¿Autenticado?
    ├─→ NO
    │   ├─ Solo puede: inicio, login, registro, escanear
    │   └─ No puede: comentar, ver progreso, admin
    │
    └─→ SÍ
        ├─ ¿Es admin (is_staff)?
        │   ├─→ NO: Usuario normal
        │   │   ├─ Puede: escanear, comentar, ver progreso
        │   │   └─ No puede: admin
        │   │
        │   └─→ SÍ: Administrador
        │       ├─ Puede: TODO
        │       └─ Admin decorators apply
        │
        └─ Crear sesión segura
```

## 🎯 CICLO DE VIDA DE UN ESCANEO

```
ANTES DEL ESCANEO:
  QRCode (creado por admin)
    ├─ Código QR generado ✅
    ├─ Imagen guardada ✅
    └─ ContenidoQR asociado ✅

MOMENTO DEL ESCANEO:
  Usuario abre /escanear/
    ├─ jsQR inicia
    ├─ Cámara pedida
    ├─ Usuario apunta a QR
    ├─ UUID detectado
    └─ Redirige a /qr/<uuid>/

DESPUÉS DEL ESCANEO:
  procesar_qr() ejecuta
    ├─ Verifica si usuario autenticado
    ├─ Crea/actualiza ProgresoUsuario
    ├─ Suma +10 puntos
    ├─ Incrementa contador de QRs
    └─ Renderiza contenido_qr.html

USUARIO VE:
  ├─ Contenido multimedia
  ├─ Información educativa
  ├─ Comentarios aprobados
  ├─ Campo para nuevo comentario
  └─ Botones de navegación

DESPUÉS:
  - Usuario puede comentar
  - Su progreso está guardado
  - Puede volver a escanear
  - Verá su avance en "Mi Progreso"
```

## 🌐 RUTAS Y VISTAS

```
Ruta                           Método  Autenticación  Plantilla
─────────────────────────────────────────────────────────────────
/                              GET     Ninguna        inicio.html
/registro/                     GET/POST Ninguna       registro.html
/login/                        GET/POST Ninguna       login.html
/logout/                       GET     Requerida      redirect
/escanear/                     GET     Requerida      escanear_qr.html
/qr/<uuid>/                    GET     Requerida      contenido_qr.html
/qr/<id>/comentario/           POST    Requerida      redirect
/mi-progreso/                  GET     Requerida      mi_progreso.html
/editar-perfil/                GET/POST Requerida      editar_perfil.html

/admin/dashboard/              GET     Admin          admin/dashboard.html
/admin/qrs/                    GET     Admin          admin/qrs_list.html
/admin/qr/crear/               GET/POST Admin          admin/qr_form.html
/admin/qr/<id>/editar/         GET/POST Admin          admin/qr_form.html
/admin/qr/<id>/eliminar/       GET/POST Admin          admin/confirmar.html
/admin/qr/<id>/contenido/      GET/POST Admin          admin/contenido_form.html
/admin/comentarios/            GET     Admin          admin/comentarios.html
/admin/comentario/<id>/moderar/ GET/POST Admin          admin/moderar.html
/admin/usuarios/               GET     Admin          admin/usuarios.html
/admin/estadisticas/           GET     Admin          admin/estadisticas.html
/admin/configuracion/          GET/POST Admin          admin/config_form.html
```

## 💾 ALMACENAMIENTO DE ARCHIVOS

```
/media/
├── qrcodes/
│   └── qr_<uuid>.png         # Generados automáticamente
├── contenido/
│   ├── imagenes/
│   │   └── *.jpg, *.png
│   ├── videos/
│   │   └── *.mp4, *.webm
│   ├── audios/
│   │   └── *.mp3, *.wav
│   └── archivos/
│       └── *.pdf, *.doc
├── avatares/
│   └── *.jpg, *.png
└── logos/
    └── *.jpg, *.png
```

## ⚡ RENDIMIENTO

- SQLite para desarrollo (puedes cambiar a PostgreSQL)
- Caché de sesiones en memoria
- Índices en campos frecuentes
- Paginación para listas grandes
- Queries optimizadas con select_related/prefetch_related

## 🎓 STACK TECNOLÓGICO VISUAL

```
FRONTEND
├─ HTML5
├─ CSS3 (Bootstrap 5)
├─ JavaScript (ES6, jsQR)
└─ Font Awesome Icons

MIDDLEWARE
├─ Django ORM
├─ Sesiones
├─ CSRF Protection
└─ Authentication

BACKEND
├─ Python 3.8+
├─ Django 5.0+
├─ Pillow (Images)
├─ qrcode (QR Gen)
└─ python-dotenv

DATABASE
└─ SQLite (Dev)
   → PostgreSQL (Prod)

HOSTING
├─ DEBUG: localhost:8000
└─ PROD: Apache/Nginx + Gunicorn
```

---

¡La arquitectura está lista para producción! 🚀
