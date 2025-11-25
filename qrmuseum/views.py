from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from datetime import datetime
import json

from qrmuseum.models import (
    QRCode, ContenidoQR, Comentario, ProgresoUsuario, 
    UsuarioMuseo, MuseoConfig
)
from qrmuseum.forms import (
    RegistroUsuarioForm, QRCodeForm, ContenidoQRForm, 
    ComentarioForm, PerfilUsuarioMuseoForm, MuseoConfigForm
)


# ==================== UTILIDADES ====================

def es_admin(user):
    """Verificar si el usuario es administrador"""
    return user.is_staff or user.is_superuser


def obtener_museo_config():
    """Obtener configuración del museo o crear una por defecto"""
    config, _ = MuseoConfig.objects.get_or_create(id=1)
    return config


# ==================== VISTAS PÚBLICAS ====================

def inicio(request):
    """Página de inicio - Con opción de empezar escaneo QR o login/registro"""
    museo = obtener_museo_config()
    total_qrs = QRCode.objects.filter(activo=True).count()
    
    # Si el usuario está autenticado, mostrar su progreso
    progreso = None
    usuario_museo = None
    porcentaje_completado = 0
    
    if request.user.is_authenticated:
        try:
            usuario_museo = request.user.perfil_museo
        except UsuarioMuseo.DoesNotExist:
            usuario_museo = UsuarioMuseo.objects.create(usuario=request.user)
        
        progreso = ProgresoUsuario.objects.filter(usuario=request.user).count()
        if total_qrs > 0:
            porcentaje_completado = (progreso / total_qrs) * 100
    
    data = {
        'museo': museo,
        'total_qrs': total_qrs,
        'progreso': progreso,
        'usuario_museo': usuario_museo,
        'porcentaje_completado': int(porcentaje_completado),
        'es_usuario': request.user.is_authenticated
    }
    
    return render(request, 'inicio.html', data)


def registro(request):
    """Página de registro de usuarios"""
    if request.user.is_authenticated:
        return redirect('inicio')
    
    form = RegistroUsuarioForm()
    
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Cuenta creada exitosamente. ¡Bienvenido {usuario.first_name or usuario.username}!')
            return redirect('login')
    
    return render(request, 'registro.html', {'form': form})


def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('inicio')
    
    error = None
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido {user.first_name or user.username}!')
            return redirect('inicio')
        else:
            error = 'Usuario o contraseña incorrectos'
    
    return render(request, 'login.html', {'error': error})


def logout_view(request):
    """Cerrar sesión"""
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('inicio')


# ==================== VISTAS DE ESCANEO QR ====================

def escanear_qr(request):
    """Página para escanear un código QR"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    data = {
        'titulo': 'Escanear Código QR'
    }
    return render(request, 'escanear_qr.html', data)


def procesar_qr(request, uuid_qr):
    """Procesar el escaneo de un QR"""
    qr = get_object_or_404(QRCode, id_unico=uuid_qr, activo=True)
    
    # Registrar visita si el usuario está autenticado
    if request.user.is_authenticated:
        progreso, creado = ProgresoUsuario.objects.get_or_create(
            usuario=request.user,
            qr_visitado=qr
        )
        
        #AQUI SE DICTA EL PUNTAJE (LÍNEA 145-147)
        # Actualizar estadísticas del usuario
        try:
            usuario_museo = request.user.perfil_museo
            if creado:  # Solo si es PRIMERA VEZ que escanea este QR
                usuario_museo.total_qrs_escaneados += 1
                usuario_museo.puntos += 10  # ← SUMA 10 PUNTOS POR CADA QR NUEVO
                usuario_museo.save()  # ← Se guarda en la base de datos
        except UsuarioMuseo.DoesNotExist:
            pass
    
    # Obtener comentarios aprobados
    comentarios_aprobados = []
    if hasattr(qr, 'contenido'):
        contenido = qr.contenido
        comentarios_aprobados = contenido.comentarios.filter(moderado=True).order_by('-fecha_creacion')
    else:
        contenido = None
    
    data = {
        'qr': qr,
        'contenido': contenido,
        'comentarios_aprobados': comentarios_aprobados,
        'usuario_autenticado': request.user.is_authenticated
    }
    
    return render(request, 'contenido_qr.html', data)


@login_required(login_url='login')
def agregar_comentario(request, qr_id):
    """Agregar comentario a un contenido QR"""
    qr = get_object_or_404(QRCode, id=qr_id)
    contenido = qr.contenido
    
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.usuario = request.user
            comentario.contenido_qr = contenido
            comentario.save()
            
            # Actualizar contador de comentarios
            try:
                usuario_museo = request.user.perfil_museo
                usuario_museo.total_comentarios += 1
                usuario_museo.save()
            except UsuarioMuseo.DoesNotExist:
                pass
            
            messages.success(request, 'Comentario agregado correctamente')
            return redirect('contenido_qr', uuid_qr=qr.id_unico)
    
    return redirect('contenido_qr', uuid_qr=qr.id_unico)


@login_required(login_url='login')
def mi_progreso(request):
    """Ver progreso del usuario"""
    usuario_museo = request.user.perfil_museo if hasattr(request.user, 'perfil_museo') else None
    
    progreso_qrs = ProgresoUsuario.objects.filter(usuario=request.user).select_related('qr_visitado')
    comentarios = Comentario.objects.filter(usuario=request.user).select_related('contenido_qr')
    
    total_qrs = QRCode.objects.filter(activo=True).count()
    escaneados = progreso_qrs.count()
    porcentaje = (escaneados / total_qrs * 100) if total_qrs > 0 else 0
    
    data = {
        'usuario_museo': usuario_museo,
        'progreso_qrs': progreso_qrs,
        'comentarios': comentarios,
        'total_qrs': total_qrs,
        'escaneados': escaneados,
        'porcentaje': int(porcentaje)
    }
    
    return render(request, 'mi_progreso.html', data)


@login_required(login_url='login')
def editar_perfil(request):
    """Editar perfil de usuario"""
    usuario_museo = request.user.perfil_museo if hasattr(request.user, 'perfil_museo') else None
    
    if not usuario_museo:
        usuario_museo = UsuarioMuseo.objects.create(usuario=request.user)
    
    if request.method == 'POST':
        form = PerfilUsuarioMuseoForm(request.POST, request.FILES, instance=usuario_museo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('mi_progreso')
    else:
        form = PerfilUsuarioMuseoForm(instance=usuario_museo)
    
    data = {
        'form': form,
        'usuario_museo': usuario_museo
    }
    
    return render(request, 'editar_perfil.html', data)


# ==================== VISTAS DE ADMINISTRACIÓN ====================

def admin_required(user):
    """Decorador para verificar si el usuario es admin"""
    return user.is_staff or user.is_superuser


@login_required(login_url='login')
@user_passes_test(admin_required, login_url='inicio')
def admin_dashboard(request):
    """Panel de administración principal"""
    total_qrs = QRCode.objects.count()
    qrs_activos = QRCode.objects.filter(activo=True).count()
    total_usuarios = User.objects.count()
    total_comentarios = Comentario.objects.count()
    comentarios_pendientes = Comentario.objects.filter(moderado=False).count()
    
    data = {
        'total_qrs': total_qrs,
        'qrs_activos': qrs_activos,
        'total_usuarios': total_usuarios,
        'total_comentarios': total_comentarios,
        'comentarios_pendientes': comentarios_pendientes
    }
    
    return render(request, 'admin/dashboard.html', data)


@login_required(login_url='login')
@user_passes_test(admin_required, login_url='inicio')
def admin_qrs_list(request):
    """Lista de códigos QR para administración"""
    qrs = QRCode.objects.all().order_by('numero_secuencial')
    
    # Paginación
    paginator = Paginator(qrs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    data = {
        'page_obj': page_obj,
        'qrs': page_obj.object_list
    }
    
    return render(request, 'admin/qrs_list.html', data)


@login_required(login_url='login')
@user_passes_test(admin_required, login_url='inicio')
def admin_crear_qr(request):
    """Crear nuevo código QR"""
    if request.method == 'POST':
        form = QRCodeForm(request.POST)
        if form.is_valid():
            qr = form.save()
            messages.success(request, f'Código QR "{qr.titulo}" creado exitosamente')
            return redirect('admin_editar_qr', qr_id=qr.id)
    else:
        form = QRCodeForm()
    
    data = {
        'form': form,
        'titulo': 'Crear Nuevo Código QR',
        'action': 'crear'
    }
    
    return render(request, 'admin/qr_form.html', data)


@login_required(login_url='login')
@user_passes_test(admin_required, login_url='inicio')
def admin_editar_qr(request, qr_id):
    """Editar código QR existente"""
    qr = get_object_or_404(QRCode, id=qr_id)
    
    if request.method == 'POST':
        form = QRCodeForm(request.POST, instance=qr)
        if form.is_valid():
            form.save()
            messages.success(request, f'Código QR "{qr.titulo}" actualizado')
            return redirect('admin_qrs_list')
    else:
        form = QRCodeForm(instance=qr)
    
    # Obtener o crear contenido
    contenido = qr.contenido if hasattr(qr, 'contenido') else None
    
    data = {
        'form': form,
        'qr': qr,
        'contenido': contenido,
        'titulo': f'Editar QR: {qr.titulo}',
        'action': 'editar'
    }
    
    return render(request, 'admin/qr_form.html', data)


@login_required(login_url='login')
@user_passes_test(admin_required, login_url='inicio')
def admin_eliminar_qr(request, qr_id):
    """Eliminar código QR"""
    qr = get_object_or_404(QRCode, id=qr_id)
    
    if request.method == 'POST':
        titulo = qr.titulo
        qr.delete()
        messages.success(request, f'Código QR "{titulo}" eliminado correctamente')
        return redirect('admin_qrs_list')
    
    data = {
        'qr': qr,
        'titulo': f'Confirmar eliminación de: {qr.titulo}'
    }
    
    return render(request, 'admin/confirmar_eliminar.html', data)


@login_required(login_url='login')
@user_passes_test(admin_required, login_url='inicio')
def admin_contenido_qr(request, qr_id):
    """Crear/editar contenido de un QR"""
    qr = get_object_or_404(QRCode, id=qr_id)
    contenido = qr.contenido if hasattr(qr, 'contenido') else None
    
    if request.method == 'POST':
        form = ContenidoQRForm(request.POST, request.FILES, instance=contenido)
        if form.is_valid():
            contenido = form.save(commit=False)
            contenido.qr = qr
            contenido.save()
            messages.success(request, 'Contenido actualizado correctamente')
            return redirect('admin_editar_qr', qr_id=qr.id)
    else:
        form = ContenidoQRForm(instance=contenido)
    
    data = {
        'form': form,
        'qr': qr,
        'contenido': contenido,
        'titulo': f'Contenido para: {qr.titulo}'
    }
    
    return render(request, 'admin/contenido_form.html', data)


@login_required(login_url='login')
@user_passes_test(admin_required, login_url='inicio')
def admin_comentarios(request):
    """Gestionar comentarios (moderar)"""
    filtro = request.GET.get('filtro', 'todos')
    
    if filtro == 'pendientes':
        comentarios = Comentario.objects.filter(moderado=False)
    elif filtro == 'aprobados':
        comentarios = Comentario.objects.filter(moderado=True)
    else:
        comentarios = Comentario.objects.all()
    
    comentarios = comentarios.select_related('usuario', 'contenido_qr')
    
    # Paginación
    paginator = Paginator(comentarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    data = {
        'page_obj': page_obj,
        'filtro': filtro,
        'comentarios': page_obj.object_list
    }
    
    return render(request, 'admin/comentarios.html', data)


@login_required(login_url='login')
@user_passes_test(admin_required, login_url='inicio')
def admin_moderar_comentario(request, comentario_id):
    """Moderar un comentario (aprobar/rechazar)"""
    comentario = get_object_or_404(Comentario, id=comentario_id)
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'aprobar':
            comentario.moderado = True
            comentario.save()
            messages.success(request, 'Comentario aprobado')
        elif accion == 'rechazar':
            comentario.delete()
            messages.success(request, 'Comentario eliminado')
        
        return redirect('admin_comentarios')
    
    data = {
        'comentario': comentario,
        'titulo': 'Moderar Comentario'
    }
    
    return render(request, 'admin/moderar_comentario.html', data)


@login_required(login_url='login')
@user_passes_test(admin_required, login_url='inicio')
def admin_configuracion(request):
    """Configurar datos del museo"""
    config, _ = MuseoConfig.objects.get_or_create(id=1)
    
    if request.method == 'POST':
        form = MuseoConfigForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración del museo actualizada')
            return redirect('admin_dashboard')
    else:
        form = MuseoConfigForm(instance=config)
    
    data = {
        'form': form,
        'config': config,
        'titulo': 'Configuración del Museo'
    }
    
    return render(request, 'admin/config_form.html', data)


@login_required(login_url='login')
@user_passes_test(admin_required, login_url='inicio')
def admin_usuarios(request):
    """Gestionar usuarios del sistema"""
    usuarios = User.objects.all().select_related('perfil_museo')
    
    # Paginación
    paginator = Paginator(usuarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    data = {
        'page_obj': page_obj,
        'usuarios': page_obj.object_list
    }
    
    return render(request, 'admin/usuarios.html', data)


@login_required(login_url='login')
@user_passes_test(admin_required, login_url='inicio')
def admin_estadisticas(request):
    """Ver estadísticas del museo"""
    total_usuarios = User.objects.count()
    total_qrs = QRCode.objects.count()
    total_escaneos = ProgresoUsuario.objects.count()
    total_comentarios = Comentario.objects.count()
    
    # Top usuarios por escaneos
    top_usuarios = ProgresoUsuario.objects.values('usuario__username', 'usuario__first_name') \
        .annotate(count=Count('id')) \
        .order_by('-count')[:10]
    
    # QRs más visitados
    qrs_populares = ProgresoUsuario.objects.values('qr_visitado__titulo') \
        .annotate(count=Count('id')) \
        .order_by('-count')[:10]
    
    data = {
        'total_usuarios': total_usuarios,
        'total_qrs': total_qrs,
        'total_escaneos': total_escaneos,
        'total_comentarios': total_comentarios,
        'top_usuarios': top_usuarios,
        'qrs_populares': qrs_populares,
        'titulo': 'Estadísticas del Museo'
    }
    
    return render(request, 'admin/estadisticas.html', data)
