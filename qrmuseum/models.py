from django.db import models
from django.contrib.auth.models import User
import uuid
import qrcode
from io import BytesIO
from django.core.files import File

class MuseoConfig(models.Model):
    """Configuración del museo"""
    nombre = models.CharField(max_length=150, default="Mi Museo")
    descripcion = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=255, blank=True)
    imagen_logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    imagen_fondo = models.ImageField(upload_to='backgrounds/', blank=True, null=True, help_text="Imagen de fondo para la página")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración del Museo'
        verbose_name_plural = 'Configuración del Museo'

    def __str__(self):
        return self.nombre


class QRCode(models.Model):
    """Modelo para códigos QR del museo"""
    id_unico = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=255, blank=True)
    numero_secuencial = models.IntegerField(help_text="Número de orden en la búsqueda del tesoro")
    
    # QR
    qr_code_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    url = models.URLField(max_length=500, unique=True, editable=False)
    
    # Control
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Código QR'
        verbose_name_plural = 'Códigos QR'
        ordering = ['numero_secuencial']

    def __str__(self):
        return f"{self.numero_secuencial}. {self.titulo}"
    
    def save(self, *args, **kwargs):
        # Generar URL única basada en UUID
        if not self.url:
            self.url = f"qr://{self.id_unico}"
        
        # Generar código QR automáticamente
        if not self.qr_code_image:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            # URL del sitio donde será escaneado
            qr_url = f"{self.id_unico}/"
            qr.add_data(qr_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Guardar en memoria
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            file_name = f'qr_{self.id_unico}.png'
            self.qr_code_image.save(file_name, File(buffer), save=False)
        
        super().save(*args, **kwargs)


class ContenidoQR(models.Model):
    """Contenido multimedia asociado a cada QR"""
    TIPO_CONTENIDO = [
        ('texto', 'Texto'),
        ('imagen', 'Imagen'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('multiplo', 'Múltiple'),
    ]
    
    qr = models.OneToOneField(QRCode, on_delete=models.CASCADE, related_name='contenido')
    tipo_contenido = models.CharField(max_length=20, choices=TIPO_CONTENIDO, default='multiplo')
    titulo = models.CharField(max_length=300)
    descripcion_detallada = models.TextField()
    
    # Archivos multimedia
    imagen = models.ImageField(upload_to='contenido/imagenes/', blank=True, null=True)
    video = models.FileField(upload_to='contenido/videos/', blank=True, null=True, 
                            help_text="Formatos: MP4, WebM")
    video_url_externa = models.URLField(blank=True, null=True, 
                                        help_text="URL de video externo (YouTube, Google Drive, etc.)")
    audio = models.FileField(upload_to='contenido/audios/', blank=True, null=True,
                            help_text="Formatos: MP3, WAV, MP4")
    archivo_descarga = models.FileField(upload_to='contenido/archivos/', blank=True, null=True,
                                       help_text="PDF, documento, etc.")
    
    # Información educativa
    datos_historicos = models.TextField(blank=True, help_text="Información histórica/educativa")
    datos_cientificos = models.TextField(blank=True, help_text="Datos científicos o técnicos")
    curiosidades = models.TextField(blank=True, help_text="Curiosidades o anécdotas")
    
    # Control
    activo = models.BooleanField(default=True)
    mostrar_imagen = models.BooleanField(default=True, help_text="Mostrar imagen en el contenido")
    mostrar_video = models.BooleanField(default=True, help_text="Mostrar video en el contenido")
    mostrar_audio = models.BooleanField(default=True, help_text="Mostrar audio en el contenido")
    mostrar_archivo = models.BooleanField(default=True, help_text="Mostrar archivo descargable")
    mostrar_historico = models.BooleanField(default=True, help_text="Mostrar información histórica")
    mostrar_cientifico = models.BooleanField(default=True, help_text="Mostrar información científica")
    mostrar_curiosidades = models.BooleanField(default=True, help_text="Mostrar curiosidades")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Contenido QR'
        verbose_name_plural = 'Contenidos QR'

    def __str__(self):
        return f"Contenido: {self.qr.titulo}"
    
    def get_video_url_embed(self):
        """Convierte URL de video a formato embed para plataformas conocidas"""
        if not self.video_url_externa:
            return None
        
        url = self.video_url_externa.strip()
        
        # YouTube - Extrae ID del video
        if 'youtube.com' in url or 'youtu.be' in url:
            video_id = None
            
            # Formato: youtube.com/watch?v=VIDEO_ID
            if 'watch?v=' in url:
                video_id = url.split('watch?v=')[1].split('&')[0]
            # Formato: youtu.be/VIDEO_ID
            elif 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[1].split('?')[0].split('&')[0]
            # Formato: youtube.com/embed/VIDEO_ID (ya está en embed)
            elif 'embed/' in url:
                video_id = url.split('embed/')[1].split('?')[0].split('&')[0]
            
            if video_id:
                # Retorna URL con parámetros que funcionan mejor
                return f'https://www.youtube.com/embed/{video_id}?modestbranding=1&rel=0'
            return url
        
        # Vimeo
        elif 'vimeo.com' in url:
            video_id = None
            if 'vimeo.com/' in url:
                video_id = url.split('vimeo.com/')[1].split('?')[0].split('#')[0]
            if video_id:
                return f'https://player.vimeo.com/video/{video_id}'
            return url
        
        # Google Drive
        elif 'drive.google.com' in url or 'docs.google.com' in url:
            file_id = None
            if '/d/' in url:
                file_id = url.split('/d/')[1].split('/')[0]
            if file_id:
                return f'https://drive.google.com/file/d/{file_id}/preview'
            return url
        
        # Si no es una URL conocida, devolverla tal cual
        return url
    
    def get_video_url_original(self):
        """Obtiene la URL original del video para abrir en nueva pestaña"""
        if not self.video_url_externa:
            return None
        
        url = self.video_url_externa.strip()
        
        # Asegura que sea una URL completa
        if not url.startswith('http'):
            return f'https://{url}'
        
        return url
    
    def get_youtube_video_id(self):
        """Extrae el ID de video de YouTube de una URL"""
        if not self.video_url_externa:
            return None
        
        url = self.video_url_externa.strip()
        
        # Formato: youtube.com/watch?v=VIDEO_ID
        if 'watch?v=' in url:
            return url.split('watch?v=')[1].split('&')[0]
        # Formato: youtu.be/VIDEO_ID
        elif 'youtu.be/' in url:
            return url.split('youtu.be/')[1].split('?')[0].split('&')[0]
        # Formato: youtube.com/embed/VIDEO_ID (ya está en embed)
        elif 'embed/' in url:
            return url.split('embed/')[1].split('?')[0].split('&')[0]
        
        return None


class ProgresoUsuario(models.Model):
    """Seguimiento del progreso de cada usuario en la búsqueda del tesoro"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progreso_qr')
    qr_visitado = models.ForeignKey(QRCode, on_delete=models.CASCADE, related_name='visitantes')
    fecha_visita = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(auto_now=True)
    tiempo_permanencia = models.IntegerField(default=0, help_text="Tiempo en segundos")
    
    class Meta:
        verbose_name = 'Progreso Usuario'
        verbose_name_plural = 'Progresos Usuarios'
        unique_together = ['usuario', 'qr_visitado']
        ordering = ['-fecha_visita']

    def __str__(self):
        return f"{self.usuario.username} - {self.qr_visitado.titulo}"


class Comentario(models.Model):
    """Comentarios de usuarios sobre el contenido del QR"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios_museo')
    contenido_qr = models.ForeignKey(ContenidoQR, on_delete=models.CASCADE, related_name='comentarios')
    calificacion = models.IntegerField(choices=[(i, f'{i} ⭐') for i in range(1, 6)], default=5)
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    moderado = models.BooleanField(default=False, help_text="Aprobado por administrador")
    
    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.usuario.username} - {self.contenido_qr.qr.titulo}"


class UsuarioMuseo(models.Model):
    """Perfil extendido de usuario para el museo"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_museo')
    apodo_juego = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatares/', blank=True, null=True)
    puntos = models.IntegerField(default=0)  #  AQUI SE GUARDA EL PUNTAJE - Se actualiza en views.py procesar_qr()
    nivel = models.IntegerField(default=1)
    
    # Estadísticas
    total_qrs_escaneados = models.IntegerField(default=0)
    total_comentarios = models.IntegerField(default=0)
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_ultimo_acceso = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuario Museo'
        verbose_name_plural = 'Usuarios Museo'

    def __str__(self):
        return f"{self.usuario.username} (Nivel {self.nivel})"
