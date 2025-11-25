from django.urls import path
from qrmuseum import views

urlpatterns = [
    # Vistas públicas
    path('', views.inicio, name='inicio'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Escaneo QR
    path('escanear/', views.escanear_qr, name='escanear_qr'),
    path('qr/<uuid:uuid_qr>/', views.procesar_qr, name='contenido_qr'),
    path('qr/<int:qr_id>/comentario/', views.agregar_comentario, name='agregar_comentario'),
    
    # Mi cuenta
    path('mi-progreso/', views.mi_progreso, name='mi_progreso'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    
    # Admin Museum (usando prefijo 'app' para evitar conflicto con admin de Django)
    path('app/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('app/qrs/', views.admin_qrs_list, name='admin_qrs_list'),
    path('app/qr/crear/', views.admin_crear_qr, name='admin_crear_qr'),
    path('app/qr/<int:qr_id>/editar/', views.admin_editar_qr, name='admin_editar_qr'),
    path('app/qr/<int:qr_id>/eliminar/', views.admin_eliminar_qr, name='admin_eliminar_qr'),
    path('app/qr/<int:qr_id>/contenido/', views.admin_contenido_qr, name='admin_contenido_qr'),
    path('app/comentarios/', views.admin_comentarios, name='admin_comentarios'),
    path('app/comentario/<int:comentario_id>/moderar/', views.admin_moderar_comentario, name='admin_moderar_comentario'),
    path('app/configuracion/', views.admin_configuracion, name='admin_configuracion'),
    path('app/usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('app/estadisticas/', views.admin_estadisticas, name='admin_estadisticas'),
]
