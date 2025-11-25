#!/usr/bin/env python
"""
Script de inicialización para MuseoQR
Crea admin, configuración de museo y datos de ejemplo
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkscanner.settings')
django.setup()

from django.contrib.auth.models import User
from qrmuseum.models import MuseoConfig, QRCode, ContenidoQR, UsuarioMuseo

def crear_admin():
    """Crear usuario administrador"""
    if User.objects.filter(username='admin').exists():
        print("✓ Admin ya existe")
        return User.objects.get(username='admin')
    
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@museo.local',
        password='admin123'
    )
    print("✅ Admin creado: admin / admin123")
    return admin

def crear_museo():
    """Crear configuración de museo"""
    if MuseoConfig.objects.exists():
        print("✓ Museo ya configurado")
        return MuseoConfig.objects.first()
    
    museo = MuseoConfig.objects.create(
        nombre_museo="Museo de Arte Moderno",
        descripcion_museo="Descubre las obras maestras del arte moderno a través de una aventura interactiva con códigos QR.",
        ciudad="Santiago",
        pais="Chile"
    )
    print("✅ Museo creado:", museo.nombre_museo)
    return museo

def crear_qr_ejemplo(admin, titulo, artista, info, historico):
    """Crear QR de ejemplo con contenido"""
    try:
        qr = QRCode.objects.create(
            nombre=titulo,
            codigo_uuid="qr-" + artista.lower().replace(" ", "-"),
            creado_por=admin
        )
        
        contenido = ContenidoQR.objects.create(
            qr=qr,
            informacion_general=info,
            informacion_historica=historico,
            informacion_cientifica="Técnica: Óleo sobre lienzo",
            curiosidades="Obra destacada de la colección permanente",
            mostrar_imagen=True,
            mostrar_historico=True,
            mostrar_cientifico=True,
            mostrar_curiosidades=True
        )
        
        print(f"✅ QR creado: {titulo} ({artista})")
        return qr, contenido
    except Exception as e:
        print(f"⚠️  No se pudo crear {titulo}: {e}")
        return None, None

def main():
    print("\n" + "="*60)
    print("🎭 Inicializando MuseoQR")
    print("="*60 + "\n")
    
    # Crear admin
    admin = crear_admin()
    
    # Crear configuración de museo
    museo = crear_museo()
    
    # Crear QRs de ejemplo
    print("\n📝 Creando QRs de ejemplo...\n")
    
    ejemplos = [
        {
            "titulo": "El Grito",
            "artista": "Edvard Munch",
            "info": "Uno de los cuadros más famosos de la historia del arte. Representa la angustia existencial del ser humano moderno.",
            "historico": "Pintado en 1893, es una obra maestra del expresionismo. Munch capturó la ansiedad y el miedo universal."
        },
        {
            "titulo": "La Persistencia de la Memoria",
            "artista": "Salvador Dalí",
            "info": "Obra maestra del surrealismo que desafía la percepción convencional del tiempo con sus famosos relojes derretidos.",
            "historico": "Creada en 1931, esta obra representa los sueños y el inconsciente según la teoría freudiana del propio Dalí."
        },
        {
            "titulo": "Guernica",
            "artista": "Pablo Picasso",
            "info": "Pintura mural de gran formato que expresa el horror de la guerra. Uno de los cuadros más poderosos del siglo XX.",
            "historico": "Creado en 1937 en respuesta al bombardeo de Guernica durante la Guerra Civil Española."
        }
    ]
    
    for ejemplo in ejemplos:
        crear_qr_ejemplo(admin, **ejemplo)
    
    print("\n" + "="*60)
    print("✅ Inicialización completada")
    print("="*60)
    print("\n📊 Estadísticas:")
    print(f"   • Users: {User.objects.count()}")
    print(f"   • QRs: {QRCode.objects.count()}")
    print(f"   • Contenido: {ContenidoQR.objects.count()}")
    print(f"   • Museo: {MuseoConfig.objects.count()}")
    print("\n🔐 Credenciales de admin:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("\n🌐 URLs importantes:")
    print("   • Inicio: http://localhost:8000/")
    print("   • Escanear QR: http://localhost:8000/escanear/")
    print("   • Dashboard Admin: http://localhost:8000/app/dashboard/")
    print("   • Admin Django: http://localhost:8000/admin/")
    print("\n")

if __name__ == '__main__':
    main()
