from django.contrib import admin
from qrmuseum.models import MuseoConfig, QRCode, ContenidoQR, Comentario, ProgresoUsuario, UsuarioMuseo


@admin.register(MuseoConfig)
class MuseoConfigAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ubicacion', 'fecha_creacion']
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'ubicacion', 'imagen_logo')
        }),
        ('Control', {
            'fields': ('fecha_creacion', 'fecha_actualizacion')
        }),
    )
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['numero_secuencial', 'titulo', 'ubicacion', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['titulo', 'descripcion']
    readonly_fields = ('id_unico', 'url', 'qr_code_image', 'fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información General', {
            'fields': ('titulo', 'descripcion', 'ubicacion', 'numero_secuencial')
        }),
        ('Código QR', {
            'fields': ('id_unico', 'url', 'qr_code_image')
        }),
        ('Control', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )


@admin.register(ContenidoQR)
class ContenidoQRAdmin(admin.ModelAdmin):
    list_display = ['qr', 'tipo_contenido', 'activo', 'fecha_creacion']
    list_filter = ['tipo_contenido', 'activo', 'fecha_creacion']
    search_fields = ['titulo', 'descripcion_detallada']
    
    fieldsets = (
        ('Contenido Principal', {
            'fields': ('qr', 'tipo_contenido', 'titulo', 'descripcion_detallada')
        }),
        ('Archivos Multimedia', {
            'fields': ('imagen', 'video', 'audio', 'archivo_descarga')
        }),
        ('Información Educativa', {
            'fields': ('datos_historicos', 'datos_cientificos', 'curiosidades')
        }),
        ('Control', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'contenido_qr', 'calificacion', 'moderado', 'fecha_creacion']
    list_filter = ['moderado', 'calificacion', 'fecha_creacion']
    search_fields = ['usuario__username', 'texto']
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Comentario', {
            'fields': ('usuario', 'contenido_qr', 'calificacion', 'texto')
        }),
        ('Moderación', {
            'fields': ('moderado',)
        }),
        ('Control', {
            'fields': ('fecha_creacion', 'fecha_actualizacion')
        }),
    )


@admin.register(ProgresoUsuario)
class ProgresoUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'qr_visitado', 'fecha_visita', 'tiempo_permanencia']
    list_filter = ['fecha_visita']
    search_fields = ['usuario__username', 'qr_visitado__titulo']
    readonly_fields = ('fecha_visita', 'fecha_completado')


@admin.register(UsuarioMuseo)
class UsuarioMuseoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'apodo_juego', 'puntos', 'nivel', 'total_qrs_escaneados']
    list_filter = ['nivel', 'fecha_registro']
    search_fields = ['usuario__username', 'apodo_juego']
    readonly_fields = ('fecha_registro', 'fecha_ultimo_acceso')
